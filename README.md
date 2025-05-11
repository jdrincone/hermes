# Hermes - Sistema de Formularios de Calidad y Producción

Este es un sistema de formularios desarrollado con Streamlit que permite gestionar formularios de calidad y producción, con diferentes niveles de acceso según el rol del usuario.

## Características

- Sistema de autenticación de usuarios
- Formularios de calidad y producción
- Diferentes niveles de acceso según el rol del usuario
- Almacenamiento de respuestas en base de datos SQLite
- Validación de respuestas numéricas y categóricas
- Interfaz intuitiva y fácil de usar

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd hermes
```

2. Crear un entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

1. La base de datos se creará automáticamente al ejecutar la aplicación por primera vez.
2. Para crear usuarios iniciales, puedes usar el siguiente script de Python:

```python
from database import get_db
from auth import create_user
from models import UserRole

db = next(get_db())
create_user(db, "admin", "admin123", UserRole.ADMIN)
create_user(db, "supervisor", "super123", UserRole.SUPERVISOR)
create_user(db, "operator", "oper123", UserRole.OPERATOR)
```

## Ejecución

Para iniciar la aplicación:

```bash
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

## Estructura del Proyecto

- `app.py`: Aplicación principal de Streamlit
- `models.py`: Modelos de base de datos
- `auth.py`: Utilidades de autenticación
- `database.py`: Configuración de la base de datos
- `config.py`: Configuración de preguntas y categorías

## Roles de Usuario

- **Admin**: Acceso completo a todas las preguntas y categorías
- **Supervisor**: Acceso a un conjunto limitado de preguntas
- **Operador**: Acceso a preguntas básicas

## Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

# Hermes Modular App

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

## Estructura Modular
- Agrega o quita formularios editando `config/forms_config.py` y los archivos en `forms/`.
- Agrega o quita preguntas solo editando `config/forms_config.py`.

## Dependencias
- Streamlit
- SQLAlchemy
- Passlib
- Bcrypt 