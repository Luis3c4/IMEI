# Estructura del Proyecto IMEI (Backend)

Este documento describe la estructura del proyecto IMEI, que contiene el backend de la aplicación.

```
IMEI/
├── .gitignore
├── credentials.json
├── legacy.app.py
├── run.py
└── app/
    ├── __init__.py
    ├── config.py
    ├── __pycache__/
    ├── routes/
    │   ├── __init__.py
    │   ├── devices.py
    │   ├── health.py
    │   ├── sheets.py
    │   └── __pycache__/
    ├── services/
    │   ├── dhru_service.py
    │   ├── sheets_service.py
    │   └── __pycache__/
    └── utils/
        ├── parsers.py
        ├── validators.py
        └── __pycache__/
```

## Descripción de los archivos y carpetas principales

- **.gitignore**: Archivo para ignorar archivos en el control de versiones.
- **credentials.json**: Archivo de credenciales (probablemente para APIs o servicios externos).
- **legacy.app.py**: Archivo de aplicación legacy (posiblemente una versión anterior).
- **run.py**: Script principal para ejecutar la aplicación.
- **app/**: Carpeta principal de la aplicación.
  - **__init__.py**: Inicialización del paquete Python.
  - **config.py**: Configuraciones de la aplicación.
  - **__pycache__/**: Archivos compilados de Python (generados automáticamente).
  - **routes/**: Definiciones de rutas/endpoints de la API.
    - **devices.py**: Rutas relacionadas con dispositivos.
    - **health.py**: Rutas de salud/verificación del sistema.
    - **sheets.py**: Rutas para integración con Google Sheets.
  - **services/**: Lógica de negocio y servicios externos.
    - **dhru_service.py**: Servicio para integración con DHRU.
    - **sheets_service.py**: Servicio para Google Sheets.
  - **utils/**: Utilidades y helpers.
    - **parsers.py**: Funciones para parsear datos.
    - **validators.py**: Validaciones de datos.

# Diagrama de Arquitectura - IMEI Backend

## Estructura en Capas

```
┌─────────────────────────────────────────────┐
│            API / PRESENTACIÓN               │
│              (Flask Routes)                 │
│  Maneja requests HTTP y responses JSON     │
└────────────────┬────────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
┌────────▼────────┐  ┌──▼──────────────┐
│   RUTAS / BP    │  │   SERVICIOS     │
├─────────────────┤  ├─────────────────┤
│ • devices_bp    │  │ • DHRUService   │
│ • health_bp     │  │ • SheetsService │
│ • sheets_bp     │  │                 │
│ Endpoints REST  │  │ Lógica negocio │
└────────┬────────┘  └────────┬────────┘
         │                    │
         └────────┬───────────┘
                  │
         ┌────────▼────────────┐
         │   INTEGRACIONES     │
         ├────────────────────┤
         │  DHRU Fusion API    │
         │  Google Sheets API  │
         │                     │
         │ • Consultas IMEI    │
         │ • Balance cuenta    │
         │ • Historial datos   │
         └─────────────────────┘
```

## Estructura de Archivos

```
app/
│
├── __init__.py                      [FABRICA DE APP]
│   ├─ create_app()
│   ├─ Configura CORS
│   ├─ Registra blueprints
│   └─ Inicializa Sheets
│
├── config.py                        [CONFIGURACIONES]
│   ├─ Settings con Pydantic
│   ├─ API keys (DHRU, Google)
│   ├─ Configs por entorno
│   └─ Variables de entorno
│
├── routes/                          [ENDPOINTS API]
│   ├── __init__.py                 [REGISTRO BLUEPRINTS]
│   │   ├─ register_blueprints()
│   │   └─ Prefijos URL
│   │
│   ├── devices.py                  [CONSULTAS DISPOSITIVOS]
│   │   ├─ POST /api/devices/consultar
│   │   ├─ Valida input
│   │   ├─ Consulta DHRU
│   │   └─ Guarda en Sheets
│   │
│   ├── health.py                   [VERIFICACIÓN SISTEMA]
│   │   └─ GET /api/health
│   │
│   └── sheets.py                   [ESTADÍSTICAS SHEETS]
│       ├─ GET /api/sheets/stats
│       ├─ GET /api/sheets/balance
│       ├─ GET /api/sheets/services
│       └─ GET /api/sheets/last-order
│
├── services/                        [LÓGICA DE NEGOCIO]
│   ├── dhru_service.py             [INTEGRACIÓN DHRU]
│   │   ├─ query_device()
│   │   ├─ get_balance()
│   │   ├─ Manejo timeouts
│   │   └─ Normalización datos
│   │
│   └── sheets_service.py           [INTEGRACIÓN SHEETS]
│       ├─ add_record()
│       ├─ initialize_sheet()
│       ├─ Autenticación OAuth
│       └─ Gestión worksheet
│
└── utils/                           [UTILIDADES]
    ├── parsers.py                  [PARSEADORES]
    │   ├─ normalize_keys()
    │   └─ Formateo datos
    │
    └── validators.py               [VALIDADORES]
        ├─ IMEIValidator
        ├─ SerialValidator
        ├─ DeviceInputValidator
        └─ Algoritmo Luhn
```

## Flujo de Datos

### Consulta de Dispositivo

```
Cliente POST /api/devices/consultar
        ↓
routes/devices.py: query_device()
        ↓
DeviceInputValidator.validate()
        ↓
DHRUService.query_device()
        ↓
API DHRU Fusion (GET con params)
        ↓
Respuesta JSON de DHRU
        ↓
normalize_keys() + parseo
        ↓
SheetsService.add_record()
        ↓
Google Sheets API (append row)
        ↓
Respuesta JSON al cliente
        ↓
Incluye: device_info + sheet_url + total_registros
```

### Carga de Estadísticas

```
Cliente GET /api/sheets/stats
        ↓
routes/sheets.py: get_stats()
        ↓
SheetsService.get_stats()
        ↓
Google Sheets API (read range)
        ↓
Cuenta filas + última consulta
        ↓
Respuesta JSON con stats
```

### Obtención de Balance

```
Cliente GET /api/sheets/balance
        ↓
routes/sheets.py: get_balance()
        ↓
DHRUService.get_balance()
        ↓
API DHRU (GET balance)
        ↓
Respuesta float balance
```

## Validación de Entrada

```
Input recibido en endpoint
        ↓
DeviceInputValidator.validate()
        ↓
¿Tipo válido?
        ├─ IMEI (15 dígitos + Luhn)
        ├─ Serial (S[A-Z0-9]{8,})
        └─ Otro → Error 400
        ↓
¿Formato correcto?
        ├─ IMEI: Algoritmo Luhn
        ├─ Serial: Patrón regex
        └─ Otro → Error 400
```

## Endpoints API

```
POST /api/devices/consultar
├─ Body: { input_value, service_id?, formato? }
├─ Valida: IMEI/Serial
├─ Consulta: DHRU API
├─ Guarda: Google Sheets
└─ Response: { success, data?, error?, sheet_url?, total_registros? }

GET /api/sheets/stats
├─ Lee: Google Sheets
├─ Calcula: total_consultas, ultima_consulta
└─ Response: { total_consultas, sheet_existe, sheet_url, ultima_consulta }

GET /api/sheets/balance
├─ Consulta: DHRU API
└─ Response: { balance }

GET /api/sheets/services
└─ Response: Service[] (hardcoded)

GET /api/sheets/last-order
├─ Lee: última fila Sheets
└─ Response: { precio, order_id }

GET /api/health
└─ Response: { status: "ok" }
```