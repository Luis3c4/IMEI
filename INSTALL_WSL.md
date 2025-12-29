# Guía de Instalación - WSL

## Problema Resuelto
Se han limpiado las dependencias duplicadas y se ha optimizado `requirements.txt` con solo las bibliotecas necesarias para el proyecto.

## Dependencias del Proyecto

### Bibliotecas Python utilizadas:
- **FastAPI**: Framework web principal
- **Uvicorn**: Servidor ASGI
- **Pydantic**: Validación de datos
- **Requests/HTTPX**: Cliente HTTP
- **Gspread + Google APIs**: Integración con Google Sheets
- **Weasyprint**: Generación de PDFs
- **Jinja2**: Motor de templates para PDFs

## Instalación en WSL/Ubuntu

### Opción 1: Script Automático (Recomendado)

```bash
# Dar permisos de ejecución al script
chmod +x install_dependencies.sh

# Ejecutar el script
./install_dependencies.sh
```

### Opción 2: Instalación Manual

#### 1. Instalar dependencias del sistema para Weasyprint

```bash
sudo apt-get update

sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info
```

#### 2. Crear y activar entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

#### 3. Instalar dependencias Python

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar requirements
pip install -r requirements.txt
```

## Verificar Instalación

```bash
# Verificar que weasyprint se instaló correctamente
python -c "import weasyprint; print('Weasyprint OK')"

# Verificar todas las dependencias
python -c "import fastapi, gspread, weasyprint, jinja2; print('✅ Todas las dependencias instaladas')"
```

## Iniciar el Servidor

```bash
# Activar entorno virtual (si no está activo)
source venv/bin/activate

# Opción 1: Usar main.py
python main.py

# Opción 2: Usar uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Solución de Problemas Comunes

### Error: "cannot import name 'HTML' from 'weasyprint'"

Asegúrate de tener instaladas las dependencias del sistema:
```bash
sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

### Error: "ModuleNotFoundError: No module named 'cairo'"

Instala python3-cffi y libffi-dev:
```bash
sudo apt-get install python3-cffi libffi-dev
pip install --upgrade cairocffi
```

### Error con Google Sheets

Asegúrate de tener el archivo `credentials.json` en la raíz del proyecto o la variable de entorno `GOOGLE_CREDENTIALS_JSON` configurada.

## Estructura de Archivos Limpia

```
IMEI/
├── requirements.txt          # ✅ LIMPIO - Solo dependencias necesarias
├── install_dependencies.sh   # ✅ Script de instalación
├── main.py
├── credentials.json
└── app/
    ├── services/
    │   ├── dhru_service.py
    │   ├── sheets_service.py
    │   └── invoice_pdf_service.py
    └── routes/
```

## Notas Importantes

- ✅ Se eliminó `requirements_clean.txt` (duplicado)
- ✅ Se limpiaron paquetes del sistema Ubuntu/WSL innecesarios
- ✅ Se agregaron solo las versiones estables y necesarias
- ✅ Weasyprint y todas sus dependencias están configuradas correctamente

## Próximos Pasos

1. Ejecutar el script de instalación
2. Activar el entorno virtual
3. Iniciar el servidor
4. Probar la generación de PDFs
