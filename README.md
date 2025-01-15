
---

### Django (Backend) README

```markdown
# Django Backend

## Description
This repository contains the backend API for the project, built with Django and Django REST Framework (DRF).

---

## Ignore the App folder

## Dependencies
The following dependencies are required for the project:

### Core Dependencies
- `django`: High-level Python web framework.
- `djangorestframework`: Toolkit for building Web APIs.
- `python-decouple`: For managing configuration settings securely.
- `django-cors-headers`: For enabling CORS (Cross-Origin Resource Sharing).

### Database
- `psycopg2`: PostgreSQL database adapter for Python.

### Authentication
- `django-rest-framework-simplejwt`: JWT-based authentication.

### Development Tools
- `django-debug-toolbar`: For debugging Django applications.
- `pytest-django`: For testing Django applications.

### Other Libraries
- `gunicorn`: WSGI HTTP server for deployment.
- `whitenoise`: For serving static files in production.

---

## Installation
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver

### Ignore the App folder
