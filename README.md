# IMEI - Sistema de Consulta de Dispositivos

Sistema de API REST en **FastAPI** (Python) para consultar información de dispositivos IMEI y registrar el historial en Google Sheets.

## 📋 Descripción del Proyecto

Esta aplicación permite:
- **Consultar información de dispositivos** usando su IMEI
- **Obtener balance de cuenta** en la API DHRU
- **Registrar historial de consultas** en Google Sheets
- **Obtener servicios disponibles** para la consulta
- **Buscar en historial** de consultas previas
- **Documentación automática** con Swagger UI

## 🚀 Instalación

### Requisitos Previos
- Python 3.10+
- pip (gestor de paquetes de Python)
- Credenciales de Google Cloud (archivo JSON)
- Clave API de DHRU

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <repo-url>
cd IMEI
```

2. **Crear entorno virtual** (opcional pero recomendado)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
Crear archivo `.env` en la raíz del proyecto:
```env
DHRU_API_KEY=tu_api_key
DHRU_API_USER=tu_email@gmail.com
GOOGLE_SHEET_ID=tu_google_sheet_id
GOOGLE_CREDENTIALS_JSON=ruta_o_contenido_del_archivo_json
```

5. **Ejecutar la aplicación**
```bash
python main.py
```

La aplicación estará disponible en `http://localhost:8000`

**Documentación interactiva:** `http://localhost:8000/docs`

## 📦 Librerías Utilizadas

### Framework Web (Principal)
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno y rápido para Python (sucesor de Flask)
- **[Uvicorn](https://www.uvicorn.org/)** - Servidor ASGI de alta performance

### Validación y Configuración
- **[Pydantic](https://docs.pydantic.dev/)** - Validación de datos y modelos con type hints
- **[pydantic-settings](https://docs.pydantic.dev/latest/concepts/settings/)** - Gestión de configuración basada en Pydantic

### Google Sheets y Autenticación
- **[gspread](https://docs.gspread.org/)** - Cliente Python para Google Sheets
- **[google-auth-oauthlib](https://google-auth-oauthlib.readthedocs.io/)** - Autenticación OAuth2 de Google
- **[google-auth-httplib2](https://github.com/googleapis/google-auth-library-python-httplib2)** - Biblioteca HTTP para autenticación de Google
- **[google-api-python-client](https://github.com/googleapis/google-api-python-client)** - Cliente API de Google

### Peticiones HTTP
- **[requests](https://requests.readthedocs.io/)** - Biblioteca para hacer peticiones HTTP
- **[httpx](https://www.python-httpx.org/)** - Cliente HTTP asíncrono (alternativa moderna a requests)

### Utilidades
- **[python-dotenv](https://python-dotenv.readthedocs.io/)** - Cargar variables de entorno desde .env

## 🔌 APIs Externas

### 1. DHRU API
**Base URL:** `https://sickw.com/api.php`

Proporciona información detallada sobre dispositivos móviles usando su IMEI.

#### Acciones Principales:
- **balance** - Obtener balance de la cuenta
- **services** - Listar servicios disponibles
- **query** - Consultar información del dispositivo
- **history** - Buscar en historial de consultas

#### Documentación:
Contactar al proveedor para más información sobre endpoints y parámetros específicos.

### 2. Google Sheets API
**URL:** `https://www.googleapis.com/auth/spreadsheets`

Se utiliza para:
- Registrar historial de consultas de dispositivos
- Obtener estadísticas de consultas
- Almacenar información de dispositivos consultados

#### Scopes Utilizados:
```
https://www.googleapis.com/auth/spreadsheets
https://www.googleapis.com/auth/drive
```

**Documentación:** [Google Sheets API Docs](https://developers.google.com/sheets/api)

### 3. Google Drive API
**URL:** `https://www.googleapis.com/auth/drive`

Se utiliza para acceder y gestionar los archivos de Google Sheets.

**Documentación:** [Google Drive API Docs](https://developers.google.com/drive/api)

## 📁 Estructura del Proyecto

```
IMEI/
├── app/
│   ├── __init__.py              # Inicialización de la app Flask
│   ├── config.py                # Configuración y variables de entorno
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── devices.py           # Rutas para consulta de dispositivos
│   │   ├── health.py            # Rutas de salud de la aplicación
│   │   └── sheets.py            # Rutas para Google Sheets
│   ├── services/
│   │   ├── dhru_service.py      # Servicio DHRU API
│   │   └── sheets_service.py    # Servicio Google Sheets
│   └── utils/
│       ├── parsers.py           # Funciones de parseo
│       └── validators.py        # Funciones de validación
├── run.py                       # Punto de entrada de la aplicación
├── legacy.app.py                # Código legacy (referencia)
├── credentials.json             # Credenciales de Google (NO committer)
├── .env                         # Variables de entorno (NO committer)
├── .gitignore
└── README.md
```

## 🔌 Endpoints de API

### 1. Health Check
Verificar que el servidor esté funcionando

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/health` | Verifica que el servidor esté funcionando correctamente |

**Ejemplo de respuesta:**
```json
{
  "status": "ok",
  "message": "Servidor funcionando correctamente",
  "api_provider": "DHRU Fusion (sickw.com)",
  "timestamp": "2025-12-27T10:30:00.000000"
}
```

---

### 2. Dispositivos (Devices)

#### 2.1 Consultar Dispositivo
Consulta información detallada de un dispositivo usando su IMEI

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/devices/consultar` | Consulta información de dispositivo por IMEI |

**Body JSON:**
```json
{
  "input_value": "356789012345678",      // IMEI del dispositivo (requerido)
  "service_id": "30",                     // ID del servicio (opcional, por defecto: 30)
  "formato": "beta"                       // Formato de respuesta (opcional)
}
```

**Ejemplo de respuesta:**
```json
{
  "success": true,
  "data": {
    "serial_number": "RF123456789",
    "model_description": "iPhone 14 Pro Max",
    "imei": "356789012345678",
    "warranty_status": "Valid",
    "purchase_country": "US",
    "sim_lock_status": "Unlocked"
  },
  "balance": 150.50,
  "price": 0.50,
  "order_id": "12345",
  "sheet_updated": true,
  "total_registros": 45,
  "sheet_url": "https://docs.google.com/spreadsheets/d/..."
}
```

---

#### 2.2 Obtener Balance
Verifica el balance disponible en la cuenta DHRU

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/devices/balance` | Obtiene el balance de la cuenta |
| `POST` | `/api/devices/balance` | Obtiene el balance de la cuenta |

**Ejemplo de respuesta:**
```json
{
  "success": true,
  "balance": 150.50,
  "message": "Balance obtenido correctamente"
}
```

---

#### 2.3 Obtener Servicios Disponibles
Lista todos los servicios disponibles en DHRU

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/devices/services` | Obtiene lista de servicios disponibles |
| `POST` | `/api/devices/services` | Obtiene lista de servicios disponibles |

**Ejemplo de respuesta:**
```json
{
  "success": true,
  "services": [
    {
      "id": "30",
      "name": "iCloud Status",
      "price": "0.50"
    },
    {
      "id": "31",
      "name": "Samsung Find My Mobile",
      "price": "0.75"
    }
  ],
  "total": 50,
  "message": "Servicios obtenidos correctamente"
}
```

---

#### 2.4 Buscar en Historial
Busca en el historial de órdenes por IMEI o Order ID

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/devices/historial` | Busca en historial de consultas |

**Body JSON:**
```json
{
  "imei_o_order_id": "356789012345678",  // IMEI o Order ID (requerido)
  "formato": "beta"                       // Formato de respuesta (opcional)
}
```

**Ejemplo de respuesta:**
```json
{
  "success": true,
  "data": {
    "orders": [
      {
        "id": "12345",
        "imei": "356789012345678",
        "service": "iCloud Status",
        "price": "0.50",
        "date": "2024-01-15 10:30:00",
        "status": "completed"
      }
    ]
  },
  "message": "Historial obtenido"
}
```

---

### 3. Google Sheets

#### 3.1 Obtener Estadísticas
Obtiene estadísticas del Google Sheet

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/sheets/stats` | Obtiene estadísticas del Sheet |

**Ejemplo de respuesta:**
```json
{
  "success": true,
  "total_consultas": 150,
  "ultima_consulta": "2024-01-15 14:30:00",
  "sheet_url": "https://docs.google.com/spreadsheets/d/...",
  "sheet_existe": true
}
```

---

#### 3.2 Obtener URL del Sheet
Devuelve la URL y ID del Google Sheet

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/sheets/url` | Obtiene URL e ID del Google Sheet |

**Ejemplo de respuesta:**
```json
{
  "url": "https://docs.google.com/spreadsheets/d/1e1P39zCbyfPD7jg_RbnEAzm_ZfOe7B5_VDVBQCZnjZM/edit",
  "sheet_id": "1e1P39zCbyfPD7jg_RbnEAzm_ZfOe7B5_VDVBQCZnjZM"
}
```

---

## 📊 Resumen de Endpoints

| Categoría | Total |
|-----------|-------|
| Health Check | 1 |
| Dispositivos | 4 |
| Google Sheets | 2 |
| **Total** | **7** |

## 🔐 Seguridad

⚠️ **Importante:**
- Nunca committer el archivo `credentials.json` al repositorio
- Nunca committer el archivo `.env` con credenciales reales
- Usar variables de entorno para credenciales en producción
- Las credenciales de Google deben estar protegidas

## 📝 Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DHRU_API_KEY` | Clave de API de DHRU | `1PA-6X8-BMQ-T28-X6H-8WP-7CL-GTK` |
| `DHRU_API_USER` | Email de usuario DHRU | `javie.apaza@gmail.com` |
| `GOOGLE_SHEET_ID` | ID del Google Sheet | `1e1P39zCbyfPD7jg_...` |
| `GOOGLE_CREDENTIALS_JSON` | Credenciales de Google (JSON o ruta) | - |
| `DEBUG` | Modo debug | `False` |
| `HOST` | Host de la aplicación | `0.0.0.0` |
| `PORT` | Puerto de la aplicación | `5000` |
| `REDIS_URL` | URL de Redis (opcional) | `None` |

## 🛠️ Desarrollo

### Ejecutar en modo desarrollo
```bash
python main.py
```

El servidor incluye:
- 🔄 Auto-reload en cambios de código
- 📚 Documentación automática en `/docs`
- 🔍 Validación automática de datos

### Documentación Interactiva
```
Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
OpenAPI:     http://localhost:8000/openapi.json
```

### Estructura de Servicios
- **DHRUService** - Maneja todas las llamadas a la API de DHRU
- **SheetsService** - Maneja todas las operaciones con Google Sheets

### Stack Tecnológico Actual
```
Frontend:    React/TSX
Backend:     FastAPI (Python)
BD:          Google Sheets (+ opción de Supabase)
APIs:        DHRU, Google Sheets API
```

## 📚 Recursos Útiles

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gspread Documentation](https://docs.gspread.org/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/settings/)
- [Requests Library](https://requests.readthedocs.io/)

## 📄 Licencia

[Especificar licencia del proyecto]

## 👥 Autores

- Javi Apaza

## 📧 Contacto

Para preguntas o problemas, contactar a: javie.apaza@gmail.com

---

**Última actualización:** 27 de diciembre de 2025
