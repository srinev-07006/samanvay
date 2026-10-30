@echo off
TITLE SAMANVAY Launch Script
COLOR 0A
cls

echo ========================================================
echo          SAMANVAY - Unified Complaint Radar
echo               SIH 2026 Prototype Launcher
echo ========================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running or not installed.
    echo Please start Docker Desktop and run this script again.
    pause
    exit /b %errorlevel%
)

echo [1/5] Stopping any existing containers...
docker-compose down >nul 2>&1

echo [2/5] Building and starting Docker containers (Postgres, Backend, Frontend)...
docker-compose up -d --build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Docker containers.
    pause
    exit /b %errorlevel%
)

echo [3/5] Waiting for PostgreSQL to be ready...
:WAITLOOP
docker exec samanvay_db pg_isready -U postgres >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 3 /nobreak >nul
    goto WAITLOOP
)

echo [4/5] Running database migrations...
docker-compose exec -T backend alembic -c alembic.ini upgrade head

echo [5/5] Seeding initial demo institutions, cases, and users...
docker-compose exec -T backend python -m app.seed

echo.
echo ========================================================
echo           SAMANVAY is successfully running!
echo ========================================================
echo.
echo Frontend UI : http://localhost:3000
echo Backend API : http://localhost:8000
echo API Docs    : http://localhost:8000/docs
echo.
echo Opening browser to http://localhost:3000...
start http://localhost:3000

echo.
echo Press any key to stop all containers and exit...
pause >nul

echo Stopping containers...
docker-compose down
echo Done.
