# 🧪 Bruno API Test Collection

Este directorio contiene las pruebas de la API REST de **SocialITEC**, gestionadas con [Bruno](https://usebruno.com/), una herramienta ligera, rápida y fácil de usar para probar endpoints HTTP y trabajar en equipo con Git.

---

## 📦 Requisitos

- Tener Bruno instalado en tu equipo  
  👉 Descarga desde: [Descargar Bruno](https://usebruno.com/download)
- Haber clonado el repositorio principal del backend:  

  ```bash
  git clone https://github.com/Creator-DevOps/socialitec-backend.git
  cd socialitec-backend
  ```

---

## 🚀 Cómo abrir las pruebas en Bruno

1. Abre Bruno (la app).
2. Selecciona **"Open Collection Folder"**.
3. Elige la carpeta `bruno/` dentro del proyecto.
4. Verás carpetas como `auth`, `user`, `student`, etc. con archivos `.bru`.
5. Selecciona una prueba y haz clic en **Run ▶️**.

---

## 🛠️ Crear una nueva prueba

1. Dentro de Bruno, crea una **nueva carpeta** si es un módulo nuevo (ej: `document`).
2. Clic derecho → `New Request`.
3. Configura la petición: método (GET/POST/etc), URL, body, headers.
4. Guarda (Ctrl + S) y se generará un archivo `.bru`.
5. El archivo se guarda como texto plano en la carpeta actual.
6. **¡No olvides hacer commit de tus cambios!**

```bash
git add bruno/
git commit -m "Add new request for /api/reports"
```

---

## 🌐 Variables de entorno

Puedes definir variables como `base_url` para cambiar rápidamente de entorno:

Ejemplo: `bruno.env.json`

```json
{
  "base_url": "http://localhost:5000"
}
```

Luego en tus pruebas puedes usar:

```json
"{{base_url}}/api/login"
```

> Así puedes trabajar local o en producción cambiando solo un valor.

---

## 📁 Estructura sugerida

```bash
bruno/
├── auth/
│   ├── login.bru
│   └── logout.bru
├── student/
│   ├── get_all.bru
│   └── create.bru
├── request/
├── document/
└── README.md
```

---

## 🤝 Colaboración

- Todos los archivos `.bru` están versionados con Git.
- Se recomienda mantener las pruebas actualizadas por módulo.
- Usa nombres descriptivos como `get_all.bru`, `create_report.bru`, etc.

---

## 🧼 Buenas prácticas

- Usar `base_url` como variable.
- Dividir pruebas por módulo.
- Probar las rutas autenticadas con JWT (`Authorization: Bearer {{token}}`).
- Confirmar que los endpoints estén actualizados según el backend.

---

## ✨ Más info

- Documentación oficial de Bruno: [Documentación](https://docs.usebruno.com)
