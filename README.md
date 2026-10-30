# IMEI API

API REST construida con FastAPI para gestionar consultas de dispositivos y operaciones de ventas. Integra servicios externos para consultas DHRU y RENIEC, persistencia en Supabase y sincronización opcional con Google Sheets.

## Requisitos

- Docker y Docker Compose v2 (`docker compose`).
- Docker Desktop abierto si trabajas en macOS o Windows.
- Credenciales de los servicios externos que vayas a utilizar.

## Configuración inicial

Desde esta carpeta (`IMEI`), crea el archivo de configuración local:

```bash
cp .env.example .env
```

Edita `.env` y reemplaza los valores de ejemplo por las credenciales necesarias:

| Variable | Uso |
| --- | --- |
| `DHRU_API_KEY`, `DHRU_API_USER` | Consultas a DHRU. |
| `RENIEC_API_TOKEN` | Consultas al servicio RENIEC. |
| `SUPABASE_URL`, `SUPABASE_KEY` | Persistencia principal en Supabase. `SUPABASE_KEY` es una clave de backend; no la publiques ni la uses en el frontend. |
| `SUPABASE_ANON_KEY` | Opcional; validación de tokens de usuario. |
| `GOOGLE_SHEETS_CREDENTIALS`, `GOOGLE_SHEET_ID` | Sincronización opcional con Google Sheets. |
| `OCR_SERVICE_URL`, `OCR_API_KEY` | Integración opcional con el servicio OCR. |
| `REDIS_URL` | Redis externo opcional; Compose no inicia un servicio Redis. |
| `DEBUG`, `ENV` | Modo de depuración y entorno de ejecución. |

Para Google Sheets, `GOOGLE_SHEETS_CREDENTIALS` acepta el JSON de la cuenta de servicio o la ruta a un archivo JSON. Si usas un archivo, colócalo en el proyecto y configura su ruta dentro del contenedor, por ejemplo `/app/service-account.json`. Comparte la hoja con el correo de esa cuenta de servicio.

Las integraciones no configuradas pueden impedir las operaciones que dependen de ellas, aunque la API pueda iniciar. `/status` indica si Supabase y Google Sheets tienen variables configuradas; no comprueba su conectividad.

**No subas `.env` ni archivos de credenciales al repositorio.** Usa `.env.example` como plantilla, no como archivo con secretos.

## Ejecutar con Docker Compose

Los siguientes comandos se ejecutan desde la carpeta que contiene `docker-compose.yml`. El servicio publica la API en el puerto `8000` y recarga el código cuando cambian los archivos fuente.

Construir la imagen e iniciar el contenedor en segundo plano:

```bash
docker compose up --build -d
```

Comprobar el estado y consultar los logs:

```bash
docker compose ps
docker compose logs -f api
```

Reiniciar el contenedor existente:

```bash
docker compose restart api
```

Si cambiaste valores de `.env`, recrea el contenedor para que tome la nueva configuración:

```bash
docker compose up -d --force-recreate api
```

Si cambiaste dependencias o el `Dockerfile`, reconstruye y recrea el servicio:

```bash
docker compose up --build -d --force-recreate api
```

Detener y quitar el contenedor:

```bash
docker compose down
```

`docker compose down` no elimina volúmenes externos. No uses `-v` salvo que también quieras borrar los datos almacenados en volúmenes.

## Acceso y documentación

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Estado rápido: <http://localhost:8000/health>
- Configuración de integraciones: <http://localhost:8000/status>

La API agrupa operaciones de dispositivos, facturas, productos, clientes, órdenes, historial, RENIEC y transferencias. Consulta `/docs` para ver las rutas y los modelos disponibles en la versión ejecutándose.

## Estructura principal

```text
IMEI/
├── app/
│   ├── config/       # Configuración de la aplicación
│   ├── routes/       # Rutas de la API
│   └── services/     # Integraciones y lógica de servicios
├── docs/             # Documentación técnica
├── scripts/          # Utilidades de inicialización
├── Dockerfile
├── docker-compose.yml
├── main.py
├── requirements.txt
└── .env.example
```
