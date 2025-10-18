# --- Fase 1: Base ---
# Usamos una imagen oficial de Python. La versión 'slim' es más ligera, ideal para producción.
FROM python:3.11-slim

# Establecemos el directorio de trabajo dentro del contenedor.
# A partir de aquí, todos los comandos se ejecutan en /app.
WORKDIR /app

# --- Fase 2: Instalación de Dependencias ---
# Copiamos solo el archivo de requisitos primero.
# Esto aprovecha el caché de Docker: si no cambias tus dependencias,
# Docker no las reinstalará en cada build, haciendo el proceso mucho más rápido.
COPY requirements.txt .

# Instalamos las dependencias de Python.
# --no-cache-dir asegura que no se guarde caché de pip, manteniendo la imagen pequeña.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Fase 3: Copiar la Aplicación ---
# Ahora copiamos el resto del código de tu aplicación al contenedor.
COPY . .

# --- Fase 4: Configuración de Red y Ejecución ---
# Exponemos el puerto en el que correrá Uvicorn dentro del contenedor.
# Easypanel se encargará de mapear este puerto al mundo exterior.
EXPOSE 8080

# Este es el comando que se ejecutará cuando el contenedor inicie.
# Le dice a Uvicorn que corra la app 'app' que se encuentra en el archivo 'main_cadquery.py'.
# --host 0.0.0.0 es crucial para que sea accesible desde fuera del contenedor.
CMD ["uvicorn", "main_cadquery:app", "--host", "0.0.0.0", "--port", "8080"]
