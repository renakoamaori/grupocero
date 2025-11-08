# Proyecto Grupo Cero - Plataforma de Música

Desarrollé este proyecto como solución al caso de estudio "Grupo Cero" para la asignatura **PGY3121 - Programación Web** de la carrera Ingeniería en Informática en DuocUC.

## Contexto del Proyecto

Inicialmente, se trataba de un caso ficticio sobre una cooperativa de artistas plásticos que necesitaban una plataforma web para exhibir y gestionar sus obras. Sin embargo, aproveché la libertad creativa que nos dieron en la asignatura para evolucionar el concepto.

En este repositorio presento una adaptación del caso original: una plataforma web para la venta y exhibición de **música**, donde mantuve y expandí los requisitos funcionales que me solicitaron. Conservé la estructura de roles (artistas/miembros y administradores) y el flujo de aprobación de contenido, pero lo apliqué a un catálogo musical.

### Nota sobre el Historial del Repositorio

Este proyecto lo desarrollé y desplegué originalmente durante el transcurso de la asignatura en 2024, utilizando Vercel y una base de datos en Supabase. Al finalizar el ramo, el despliegue quedó inoperativo y mí repositorio original lo eliminé porque en ese entonces no consideré relevante mantenerlo público.

El código presente en este repositorio es una recuperación del proyecto original, que he reestructurado y publicado nuevamente. Por este motivo, el historial de commits es reciente y no refleja cuando realmente se desarrolló el proyecto.

### Requisitos Originales del Caso "Grupo Cero"

La plataforma que tenía que construir debía cumplir con las siguientes características:

1.  Menú superior con el logo de la cooperativa.
2.  Carrusel de imágenes con productos destacados en la página principal.
3.  Vista de detalle del producto (historia, descripción, precio, etc.) y galería de fotos.
4.  Búsqueda por nombre del artista, tipo de arte o concepto.
5.  Mostrar la cantidad de productos ingresados por un usuario.
6.  Formulario de contacto general.
7.  Acceso a productos por categoría o artista desde la página principal.
8.  Registro de usuarios (email, nombre, password).
9.  Autenticación de usuarios (email, password).
10. Indicador de estado de sesión (logueado/no logueado).
11. **Flujo de publicación de obras:**
    *   Los miembros (artistas) tienen una cuenta creada por un administrador.
    *   Tras iniciar sesión, los miembros pueden enviar nuevas obras a través de un formulario.
    *   Las obras quedan en estado pendiente hasta ser revisadas por un administrador.
    *   El administrador puede aprobar o rechazar la publicación, notificando el motivo del rechazo.
    *   El miembro puede ver el estado y la retroalimentación de sus envíos.
12. El foco es la exhibición online, no la venta directa (transacciones).
13. Diseño responsivo adaptable a móviles y escritorio.

## Descripción de la Solución que Implementé

Este proyecto es una aplicación web que desarrollé con **Django** y que funciona como una tienda de música online. Los "artistas" ahora son músicos o bandas que pueden subir sus álbumes o sencillos a la plataforma.

### Características Principales

*   **Gestión de Catálogo Musical:** Los artistas pueden proponer nuevo contenido musical, que es revisado y aprobado por un administrador.
*   **Roles de Usuario:**
    *   **Administrador:** Gestiona usuarios, aprueba o rechaza contenido y administra el sitio.
    *   **Miembro (Artista):** Sube y gestiona su propia música.
    *   **Cliente:** Se registra, navega por el catálogo y puede simular compras.
*   **Autenticación y Perfiles:** Implementé un sistema completo de registro, inicio de sesión y perfiles de usuario.
*   **Búsqueda y Filtros:** Añadí una búsqueda avanzada para encontrar música por artista, álbum o género.
*   **API REST:** Incluí una API desarrollada con Django REST Framework para la gestión de datos.
*   **Panel de Administración Personalizado:** Creé una interfaz de administración mejorada para una gestión más sencilla del contenido.

## Tecnologías que Utilicé

*   **Backend:** Python, Django
*   **Frontend:** HTML, CSS, JavaScript, Bootstrap
*   **Base de Datos:** PostgreSQL
*   **API:** Django REST Framework

## Instalación y Puesta en Marcha

Para ejecutar este proyecto en tu entorno de desarrollo local, sigue estos pasos:

1.  **Clona el repositorio:**
    ````bash
    git clone <URL_DEL_REPOSITORIO>
    cd grupocero
    ````

2.  **Crea y activa un entorno virtual:**
    ````bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ````

3.  **Instala las dependencias:**
    ````bash
    pip install -r requirements.txt
    ````

4.  **Configura las variables de entorno:**
    Renombra el archivo `.env.template` a `.env` y completa las variables necesarias.
    ````bash
    mv .env.template .env
    ````

5.  **Aplica las migraciones:**
    Este comando creará las tablas necesarias en la base de datos.
    ````bash
    python manage.py migrate
    ````

6.  **Crea un superusuario:**
    Necesitarás un superusuario para acceder al panel de administración (`/admin`).
    ````bash
    python manage.py createsuperuser
    ````

7.  **Ejecuta el servidor de desarrollo:**
    ````bash
    python manage.py runserver
    ````

    El sitio estará disponible en `http://127.0.0.1:8000`.