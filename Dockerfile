#imagen
FROM python:3.10-slim

#directorio de trabajo
WORKDIR /app

#copiar el archivo de requerimientos
COPY requirements.txt .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de tu proyecto
COPY . .

#  puerto de Flask
EXPOSE 5000

#Lanza la aplicación usando Gunicorn
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "main:app"]
