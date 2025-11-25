# ERP System in Python/Django

A complete ERP system featuring Help Desk, Timesheet, and Project Management modules.

## Features

- **Authentication**: Custom roles (Admin, Manager, Collaborator, Client).
- **Help Desk**: Ticket management with SLA, categories, and comments.
- **Timesheet**: Daily time tracking with approval workflow.
- **Projects**: Project management with Kanban board and simple Gantt chart.
- **Dashboard**: KPIs and recent activity.

## Tech Stack

### Backend

- **Language**: Python 3.11+
- **Framework**: Django 5.0+
- **API**: Django REST Framework (DRF)
- **Documentation**: Swagger / Redoc (drf-yasg)

### Database

- **Primary**: PostgreSQL 15+ (Production/Docker)
- **Development**: SQLite (Optional)
- **ORM**: Django ORM

### Frontend

- **Template Engine**: Django Templates (DTL)
- **Styling**:
  - Bootstrap 5 (Layout & Components)
  - Custom CSS (Glassmorphism & Modern UI)
  - FontAwesome 6 (Icons)
- **Interactivity**: Vanilla JavaScript

### Infrastructure & Tools

- **Containerization**: Docker & Docker Compose
- **Static Files**: WhiteNoise
- **Environment**: python-dotenv

## Installation

1. **Clone the repository**
2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Database (Docker)**

   ```bash
   docker-compose up -d
   ```

5. **Run Migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create Demo Data**

   ```bash
   python create_fixtures.py
   ```

7. **Run Server**

   ```bash
   python manage.py runserver
   ```

8. **Access**: `http://127.0.0.1:8000`
   - **Admin**: admin / admin
   - **Manager**: manager / manager
   - **Collaborator**: collab / collab
   - **Client**: client / client

## Structure

- `apps/core`: Auth & Dashboard
- `apps/helpdesk`: Ticket System
- `apps/timesheet`: Time Tracking
- `apps/projects`: Project Management
