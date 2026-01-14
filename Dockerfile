# ============================================
# DOCKERFILE PARA IMEI API - PRODUCCIÓN
# Python 3.11 con FastAPI + WeasyPrint
# ============================================

# Usar Python 3.11 slim (imagen ligera optimizada)
FROM python:3.11-slim

# Metadata del contenedor
LABEL maintainer="javie.apaza@gmail.com"
LABEL description="IMEI API - Sistema de Consulta de Dispositivos"
LABEL version="1.0"

# Variables de entorno para optimización de Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para WeasyPrint
# WeasyPrint requiere librerías de Cairo, Pango y GDK-Pixbuf para renderizar PDFs
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Librerías necesarias para WeasyPrint
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libcairo2 \
    shared-mime-info \
    # Fuentes para mejor renderizado de PDFs
    fonts-liberation \
    fonts-dejavu-core \
    # Herramientas útiles (opcional, comentar si quieres imagen más pequeña)
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar primero solo requirements.txt para aprovechar cache de Docker
# Esto evita reinstalar dependencias si solo cambió el código
COPY requirements.txt .

# Instalar dependencias de Python
# Se usa --no-cache-dir para reducir tamaño de la imagen
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copiar todo el código de la aplicación
COPY . .

# Crear usuario no-root por seguridad
# Las aplicaciones no deben ejecutarse como root en producción
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer el puerto (Railway y Render usan la variable $PORT)
EXPOSE 8000

# Health check para verificar que el contenedor está funcionando
# Docker/Railway/Render usarán esto para monitorear la salud del servicio
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Comando de inicio con Gunicorn + Uvicorn workers
# --bind 0.0.0.0:$PORT -> Escucha en todas las interfaces en el puerto especificado
# --workers 2 -> 2 procesos worker (ajustar según recursos disponibles)
# --worker-class uvicorn.workers.UvicornWorker -> Usa workers asíncronos de Uvicorn
# --timeout 120 -> Timeout de 120 segundos para requests largos
# --access-logfile - -> Logs de acceso a stdout
# --error-logfile - -> Logs de error a stdout
# --log-level info -> Nivel de logging
# Formato JSON para mejor manejo de señales del OS
CMD ["sh", "-c", "gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --access-logfile - --error-logfile - --log-level info --forwarded-allow-ips '*'"]
