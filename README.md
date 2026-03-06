# Placement Portal Application V2

## About
This is a Placement Portal web application built as a project for Modern Application Development II (MAD-II) course at IIT Madras BS Degree Program.

The application helps manage the campus placement process by connecting Students, Companies, and Admins on a single platform.

## Features
- Admin can manage students, companies, job postings and placements
- Companies can post jobs, view applications, shortlist and select candidates
- Students can view jobs, apply, track application status and view placement details
- Role based access control (Admin, Company, Student)
- Background jobs for reminders and report generation using Celery and Redis
- API caching using Redis for better performance

## Tech Stack
- **Backend:** Flask (Python)
- **Frontend:** Vue.js
- **Database:** SQLite with SQLAlchemy ORM
- **Caching:** Redis
- **Background Jobs:** Celery with Redis as broker
- **Authentication:** Flask-Security / JWT tokens

## How to Run

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run serve
```

### Redis Server
```bash
redis-server
```

### Celery Worker
```bash
celery -A app.celery worker --loglevel=info
```

### Celery Beat
```bash
celery -A app.celery beat --loglevel=info
```

## Project Structure
```
Placement Portal MAD2/
├── backend/          # Flask backend API
├── frontend/         # Vue.js frontend
├── README.md
├── .gitignore
```

## Milestones
- [x] Milestone 0: GitHub Repository Setup
- [ ] Milestone 1: Database Models and Schema Setup
- [ ] Milestone 2: Authentication and Role-Based Access
- [ ] Milestone 3: Admin Dashboard and Management
- [ ] Milestone 4: Company Dashboard and Job/Application Management
- [ ] Milestone 5: Student Dashboard and Job Application System
- [ ] Milestone 6: Job Application History and Status Tracking
- [ ] Milestone 7: Backend Jobs (Celery + Redis)
- [ ] Milestone 8: API Performance Optimization and Caching (Redis)

## Developer
- Roll Number: 23f1001305
- Course: Modern Application Development II (MAD-II)
- Term: Jan 2026
