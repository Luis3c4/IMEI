# Bug: 502 Bad Gateway en todas las rutas (Event Loop Blocking)

**Fecha:** 2026-03-20  
**Severidad:** Crítica – el servicio quedaba completamente inaccesible  
**Entorno:** Railway (producción)

---

## Síntomas observados

- `GET /api/products`, `/api/devices/services`, `/api/devices/balance` y todas las demás rutas devolvían **502 Bad Gateway**.
- El error de Railway mostraba `"connection dial timeout"` con 3 reintentos de 5000 ms cada uno (15 s total):

```json
"upstreamErrors": [
  {"error": "connection dial timeout", "duration": 5000},
  {"error": "connection dial timeout", "duration": 5000},
  {"error": "connection dial timeout", "duration": 5000}
]
```

- `"upstreamAddress": ""` → Railway ni siquiera podía abrir una conexión TCP al contenedor.
- El último log HTTP exitoso era un `GET /api/products/ 200`. Después, silencio total.
- El uso de memoria no superaba 257 MB (límite 512 MB), descartando OOM.
- El error de CORS (`No 'Access-Control-Allow-Origin' header`) era un **síntoma secundario**: la página de error 502 de Railway no incluye los headers CORS de la aplicación.

---

## Causa raíz

### El problema: llamadas síncronas bloqueantes dentro de `async def`

Todos los route handlers de FastAPI estaban declarados como `async def`, pero internamente realizaban llamadas HTTP **síncronas y bloqueantes** a servicios externos:

| Servicio | Librería usada | Tipo |
|---|---|---|
| DHRU API (consulta IMEI, balance, servicios, historial) | `requests` | Síncrono (bloqueante) |
| Supabase (productos, clientes, facturas) | `supabase-py` → `httpx.Client` | Síncrono (bloqueante) |
| WeasyPrint (generación de PDF) | librería C nativa | Síncrono (bloqueante) |

**¿Por qué esto mata el proceso?**

FastAPI corre sobre un servidor ASGI (`uvicorn`) que usa un único **event loop** de Python por worker. Cuando una función `async def` realiza una llamada síncrona bloqueante (como `requests.get(...)` o `supabase_client.table(...).execute()`), **congela el event loop completo** durante toda la duración de la llamada.

Gunicorn gestiona sus workers mediante un mecanismo de heartbeat. Si un worker no responde al heartbeat dentro del tiempo `--timeout` configurado (120 s), Gunicorn lo **mata y lo intenta reiniciar**. Con 2 workers:

1. Worker A recibe `GET /api/products` → llama a Supabase (bloqueante) → event loop congelado.
2. Worker B recibe otra petición simultánea → mismo problema.
3. Ambos workers se congelan a la vez → Gunicorn no recibe heartbeat de ninguno → los mata.
4. Mientras los workers se reinician, **nada escucha en el puerto** → Railway no puede hacer `connect()` → `connection dial timeout` × 3 → 502 en cada petición.

El tiempo exacto del crash coincidía con una carga simultánea de dos peticiones lentas (Supabase tardó más de lo normal por una breve inestabilidad de red).

---

## Solución aplicada

### 1. `dhru_service.py` — Reemplazar `requests` con `httpx` asíncrono

**Antes:**
```python
import requests

def get_balance(self) -> Dict[str, Any]:
    response = requests.get(self.base_url, params={...}, timeout=10)
    ...

def query_device(self, ...) -> Dict[str, Any]:
    response = requests.get(self.base_url, params={...}, timeout=self.timeout)
    ...
```

**Después:**
```python
import httpx

async def get_balance(self) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(self.base_url, params={...})
    ...

async def query_device(self, ...) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.get(self.base_url, params={...})
    ...
```

`httpx` ya estaba en `requirements.txt`. Los métodos `get_services` y `search_history` recibieron el mismo cambio. Los `await` correspondientes se agregaron en `devices.py`.

---

### 2. Rutas puramente síncronas — cambiar `async def` a `def`

FastAPI ejecuta los handlers `def` (no async) automáticamente en el **thread pool** de `anyio` (`run_in_executor`). Esto significa que una llamada síncrona bloqueante ocurre en un hilo separado y **nunca congela el event loop**, independientemente de cuánto tarde Supabase.

Archivos modificados:

| Archivo | Handlers cambiados |
|---|---|
| `app/routes/health.py` | `health_check` |
| `app/routes/products.py` | `get_all_products`, `create_product`, `products_health`, `bulk_toggle_items_sold`, `get_products_inventory` |
| `app/routes/customers.py` | `list_customers` |
| `app/routes/invoice_routes.py` | `generar_factura_prueba` |

**Antes:**
```python
@router.get("/")
async def get_all_products():
    result = supabase_service.products.get_products_with_variants()  # bloquea event loop
    ...
```

**Después:**
```python
@router.get("/")
def get_all_products():
    result = supabase_service.products.get_products_with_variants()  # corre en thread pool
    ...
```

---

### 3. Rutas async con `Depends` — envolver en `run_in_executor`

Las rutas que no podían convertirse a `def` (porque usan `Depends` asíncrono para autenticación JWT) envuelven sus llamadas síncronas explícitamente con `run_in_executor`:

```python
# invoice_routes.py — generar_factura_dinamica y obtener_factura_con_productos
loop = asyncio.get_running_loop()

customer_result = await loop.run_in_executor(
    None,
    lambda: supabase_service.customers.get_or_create_customer(...)
)
invoice_result = await loop.run_in_executor(
    None,
    lambda: supabase_service.invoices.create_invoice(...)
)
pdf_bytes = await loop.run_in_executor(
    None,
    lambda: invoice_service.generar_factura_dinamica(...)
)
```

Mismo patrón en `devices.py` para el guardado en Supabase tras la consulta DHRU.

---

## Regla para nuevo código

> **Si una función hace I/O (llamadas HTTP, base de datos, disco) y NO usa `await`, el handler de FastAPI debe ser `def`, no `async def`.**

| Caso | Solución correcta |
|---|---|
| Handler solo hace llamadas síncronas | `def handler()` |
| Handler usa `await` (httpx, asyncpg, etc.) | `async def handler()` |
| Handler tiene `Depends` async + llamadas síncronas | `async def` + `run_in_executor` para las partes síncronas |
| Handler no hace I/O | `def` o `async def` (indistinto) |

---

## Archivos modificados

- `app/services/dhru_service.py` — `requests` → `httpx` async
- `app/routes/devices.py` — `await` en llamadas DHRU + `run_in_executor` para Supabase
- `app/routes/health.py` — `async def` → `def`
- `app/routes/products.py` — todos los handlers `async def` → `def`
- `app/routes/customers.py` — `async def` → `def`
- `app/routes/invoice_routes.py` — `def` donde posible, `run_in_executor` donde necesario
