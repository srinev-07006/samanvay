import subprocess
import os
import time
from pathlib import Path

def run_command(cmd, shell=False):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    if result.stdout:
        print(result.stdout)
    return True

def reset_demo():
    """Reset the demo environment to initial state."""
    print("=" * 60)
    print("SAMANVAY Demo Reset Script")
    print("=" * 60)

    # 1. Stop all containers
    print("\n1. Stopping all containers...")
    if not run_command("docker-compose down"):
        print("Failed to stop containers")
        return False

    # 2. Remove volumes to ensure fresh start
    print("\n2. Removing volumes...")
    if not run_command("docker-compose down --volumes"):
        print("Failed to remove volumes")
        return False

    # 3. Build images
    print("\n3. Building Docker images...")
    if not run_command("docker-compose build"):
        print("Failed to build images")
        return False

    # 4. Start containers
    print("\n4. Starting containers...")
    if not run_command("docker-compose up -d"):
        print("Failed to start containers")
        return False

    # 5. Wait for services to be ready
    print("\n5. Waiting for services to be ready...")
    for i in range(10):
        time.sleep(5)
        # Check if PostgreSQL is ready
        try:
            result = subprocess.run(
                "docker exec samanvay_db pg_isready -U postgres",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("PostgreSQL is ready!")
                break
        except:
            pass

    # 6. Run database migrations
    print("\n6. Running database migrations...")
    if not run_command("docker-compose exec -T backend alembic -c alembic.ini upgrade head"):
        print("Failed to run migrations")
        return False

    # 7. Seed demo data
    print("\n7. Seeding demo data...")
    if not run_command("docker-compose exec -T backend python -m app.seed"):
        print("Failed to seed demo data")
        return False

    # 8. Verify data was seeded
    print("\n8. Verifying demo data...")
    try:
        # Check if there are institutions
        result = subprocess.run(
            "docker-compose exec -T backend python -c \"from app.database import get_db; from app.models import Institution; db = next(get_db()); institutions = db.query(Institution).all(); print(f'Found {len(institutions)} institutions')\"",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("Error checking institutions:", result.stderr)
            return False

        print(result.stdout)

        # Check if there are cases
        result = subprocess.run(
            "docker-compose exec -T backend python -c \"from app.database import get_db; from app.models import Case; db = next(get_db()); cases = db.query(Case).all(); print(f'Found {len(cases)} cases')\"",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("Error checking cases:", result.stderr)
            return False

        print(result.stdout)

    except Exception as e:
        print(f"Error verifying data: {e}")
        return False

    print("\n" + "=" * 60)
    print("Demo reset completed successfully!")
    print("You can now access the application at http://localhost:3000")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = reset_demo()
    exit(0 if success else 1)