# ❤️ SOCIALITEC - GESTIÓN DEL SERVICIO SOCIAL

SocialITEC es una plataforma moderna que simplifica la gestión y manejo de documentos del Servicio Social en el Instituto Tecnológico de León.

## 📋 Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- PostgreSQL
- wkhtmltopdf (para generación de PDFs)

## 🛠️ Tecnologías Principales

- **SQLAlchemy**: ORM para la base de datos
- **Boto3**: SDK de AWS para integración con S3
- **PyMuPDF**: Procesamiento de documentos PDF
- **Pydantic**: Validación de datos
- **Python-Jose**: Manejo de JWT

## 🔧 Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/Creator-DevOps/socialitec-backend.git
   ```

2. Navega al directorio del proyecto:

   ```bash
   cd socialitec-backend/app
   ```

3. Crea y activa un entorno virtual:

   ```bash
   python3 -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   ```

4. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

5. Configura las variables de entorno:
   - Crea un archivo `.env` en la carpeta `app` basándote en el ejemplo proporcionado
   - Configura las variables necesarias para tu entorno

## ⚙️ Configuración del Entorno

El archivo `.env` debe incluir las siguientes variables (ejemplo):

```env
# Configuración de la Base de Datos
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Configuración de Seguridad
SECRET_KEY=tu_clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de AWS S3
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_BUCKET_NAME=tu_bucket
AWS_REGION=tu_region

```

## 🗄️ Base de Datos

La base de datos se encuentra dentro de una instancia de EC2

## 🚀 Ejecución

1. Inicia el servidor de desarrollo:

   ```bash
   uvicorn api.main:app --reload
   ```

La aplicación estará disponible en:

- API: [http://localhost:5000](http://localhost:5000)
- Documentación: [http://localhost:5000/docs](http://localhost:5000/docs)

## 📦 Estructura del Proyecto

```bash
app/
├── api/                 # Código principal de la API
│   ├── endpoints/       # Endpoints de la API
│   ├── core/           # Configuración central
│   ├── models/         # Modelos SQLAlchemy
│   ├── schemas/        # Esquemas Pydantic
│   └── services/       # Lógica de negocio
├── static/             # Archivos estáticos
├── test/               # Pruebas
└── resources/          # Recursos adicionales
```

## 🔒 Seguridad

El sistema implementa:

- Autenticación JWT
- Roles y permisos de usuario
- Encriptación de datos sensibles
- Almacenamiento seguro de documentos

## 🤝 Contribución

1. Clona el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).
