"""
Documentación Swagger para los endpoints de administración.
Este archivo contiene la especificación OpenAPI en formato YAML para:
  - Obtener todos los administradores (GET "")
  - Obtener un administrador por ID (GET "/<int:user_id>")
  - Crear un administrador (POST "/")
  - Actualizar un administrador (PUT "/<int:user_id>")
  - Eliminar un administrador (DELETE "/<int:user_id>")
"""

get_admins_doc = """
Obtener todos los administradores
---
tags:
  - Administradores
parameters:
  - name: page
    in: query
    type: integer
    required: false
    description: Número de la página para la paginación.
  - name: limit
    in: query
    type: integer
    required: false
    description: Cantidad de elementos por página.
responses:
  200:
    description: Lista de administradores.
    schema:
      type: object
      properties:
        items:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "Admin1"
              email:
                type: string
                example: "admin1@example.com"
              position:
                type: string
                example: "Gerente"
        total:
          type: integer
          example: 2
        page:
          type: integer
          example: 1
        limit:
          type: integer
          example: 2
        pages:
          type: integer
          example: 1
  500:
    description: Error al obtener la lista de administradores.
    schema:
      type: object
      properties:
        error:
          type: string
          example: "No se pudo obtener la lista de administradores"
        details:
          type: string
          example: "Error de conexión a la base de datos"
"""

get_admin_doc = """
Obtener un administrador por ID
---
tags:
  - Administradores
parameters:
  - name: user_id
    in: path
    type: integer
    required: true
    description: ID del administrador.
responses:
  200:
    description: Administrador encontrado.
    schema:
      type: object
      properties:
        message:
          type: string
          example: "Administrador encontrado"
        data:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Admin1"
            email:
              type: string
              example: "admin1@example.com"
            position:
              type: string
              example: "Gerente"
  404:
    description: Administrador no encontrado.
    schema:
      type: object
      properties:
        message:
          type: string
          example: "Administrador no encontrado"
  500:
    description: Error al obtener el administrador.
    schema:
      type: object
      properties:
        error:
          type: string
          example: "Error al obtener administrador"
        details:
          type: string
          example: "Detalles del error"
"""

create_admin_doc = """
Crear un nuevo administrador
---
tags:
  - Administradores
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - name
        - email
        - password
        - position
      properties:
        name:
          type: string
          example: "Admin1"
        email:
          type: string
          example: "admin1@example.com"
        password:
          type: string
          example: "123456"
        position:
          type: string
          example: "Gerente"
responses:
  201:
    description: Administrador creado exitosamente.
    schema:
      type: object
      properties:
        message:
          type: string
          example: "Administrador creado"
        data:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Admin1"
            email:
              type: string
              example: "admin1@example.com"
            position:
              type: string
              example: "Gerente"
  400:
    description: Campos requeridos faltantes.
    schema:
      type: object
      properties:
        error:
          type: string
          example: "Campos requeridos faltantes: name, email, password, position"
  500:
    description: Error al crear el administrador.
    schema:
      type: object
      properties:
        error:
          type: string
          example: "No se pudo crear el administrador"
        details:
          type: string
          example: "Detalles del error"
"""

update_admin_doc = """
Actualizar un administrador
---
tags:
  - Administradores
parameters:
  - name: user_id
    in: path
    type: integer
    required: true
    description: ID del administrador a actualizar.
  - name: body
    in: body
    required: true
    schema:
      type: object
      properties:
        name:
          type: string
          example: "Admin Actualizado"
        email:
          type: string
          example: "admin_actualizado@example.com"
        position:
          type: string
          example: "Super Gerente"
responses:
  200:
    description: Administrador actualizado correctamente.
    schema:
      type: object
      properties:
        message:
          type: string
          example: "Administrador actualizado"
        data:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Admin Actualizado"
            email:
              type: string
              example: "admin_actualizado@example.com"
            position:
              type: string
              example: "Super Gerente"
  404:
    description: Administrador no encontrado.
    schema:
      type: object
      properties:
        message:
          type: string
          example: "Administrador no encontrado"
  500:
    description: Error al actualizar el administrador.
    schema:
      type: object
      properties:
        error:
          type: string
          example: "Error al actualizar"
        details:
          type: string
          example: "Detalles del error"
"""

delete_admin_doc = """
Eliminar un administrador
---
tags:
  - Administradores
parameters:
  - name: user_id
    in: path
    type: integer
    required: true
    description: ID del administrador a eliminar.
responses:
  200:
    description: Administrador eliminado correctamente.
    schema:
      type: object
      properties:
        message:
          type: string
          example: "Administrador eliminado correctamente"
  404:
    description: Administrador no encontrado.
    schema:
      type: object
      properties:
        message:
          type: string
          example: "Administrador no encontrado"
  500:
    description: Error al eliminar el administrador.
    schema:
      type: object
      properties:
        error:
          type: string
          example: "Error al eliminar"
        details:
          type: string
          example: "Detalles del error"
"""
