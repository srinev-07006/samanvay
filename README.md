# SAMANVAY - Unified Institution Complaint Radar (SIH 2026 Prototype)

## Overview
SAMANVAY is a comprehensive platform for tracking, analyzing, and resolving institution complaints across different Bureaus and Cells. It features real-time overlap detection, KPI dashboards, case history tracking, and detailed reporting capabilities.

## Features
- **Real-time Overlap Detection**: Identifies when two different Bureaus/Cells hold live cases on the same institution
- **KPI Dashboard**: Tracks total cases, pending items, processing status, and disposal rates
- **Institution Profiles**: Detailed views of institutions with complete case history and timeline
- **Side-by-side Overlap Panel**: Compare multiple cases with confidence scores and coordination requirements
- **PDF/Excel Reports**: Export case data for analysis and record-keeping
- **WebSocket Integration**: Real-time updates and alerts
- **RBAC**: Role-based access control for different user types

## Technology Stack
- **Frontend**: React, Vite, Tailwind CSS, Recharts, Lucide Icons
- **Backend**: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Database**: PostgreSQL with pg_trgm extension for text similarity matching
- **Authentication**: JWT with bcrypt password hashing
- **Background Tasks**: APScheduler for alerts and reminders
- **Reporting**: ReportLab (PDF), openpyxl (Excel)

## Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ (for development)
- Git (for cloning the repository)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/samanvay.git
cd samanvay
```

### 2. Build and Start Containers
```bash
docker-compose up -d --build
```

### 3. Run Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### 4. Seed Demo Data
```bash
docker-compose exec backend python backend/app/seed.py
```

### 5. Access the Application
Open your browser and navigate to: http://localhost:3000

## Demo Walkthrough

### Step 1: Login
- Use the quick login buttons on the login page:
  - **RB Admin**: Regulation Bureau
  - **PGRC Admin**: PGRC Cell
  - **RO West**: Regional Office
  - **Senior Mgmt**: Executive Board

### Step 2: KPI Dashboard
- View real-time case statistics
- Filter by bureau, status, or region
- Monitor overlap alerts (red banner shows "Potential Overlapping Cases – Coordination Required")

### Step 3: Institution Profile
- Select an institution to view its complete history
- See case status, assigned officer, and disposal dates
- Review the timeline of all actions taken on the institution's cases

### Step 4: Overlap Panel
- Compare two cases with the same institution ID
- View confidence scores and reasoning for overlaps
- Take action: Link, Map, or Dismiss cases

### Step 5: Reports
- Download PDF or Excel reports for case data
- Generate reports by bureau, region, or institution

## Project Structure
```
samanvay/
├── docker-compose.yml          # Container orchestration
├── backend/
│   ├── requirements.txt        # Python dependencies
│   ├── alembic/                # Database migrations
│   ├── app/
│   │   ├── models/             # Database models
│   │   ├── services/           # Business logic
│   │   ├── routers/            # FastAPI endpoints
│   │   └── main.py             # Application entry point
│   └── seed.py                 # Demo data seeding script
└── frontend/
    ├── src/
    │   ├── components/         # React components
    │   ├── services/             # API services
    │   └── App.jsx
    └── index.html
```

## Testing
Run unit tests with:
```bash
docker-compose exec backend pytest
```

## Support
For support or questions, contact the development team.

© 2026 SAMANVAY - Unified Institution Complaint Radar