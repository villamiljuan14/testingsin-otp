# Enviart Dashboard Project

A Django-based project structured for scalability and maintainability.

## Structure
- `apps/`: Contains all business logic and Django apps.
- `config/`: Main Django configuration (settings, urls, wsgi).
- `templates/`: Global HTML templates.
- `static/`: Global CSS/JS and Tailwind setup.

## Quickstart

1. Install dependencies:
   ```bash
   pip install -r requirements/base.txt
   npm install
   ```

2. Setup environment:
   ```bash
   cp .env.example .env
   # Update .env variables
   ```

3. Run migrations and server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
