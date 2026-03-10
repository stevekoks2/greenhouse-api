import os

from app.database import Base, engine
from app.models import actuator_log, sensor_data


def init_database():
    """Создание всех таблиц"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    init_database()

    # Проверяем, что файл создался
    if os.path.exists("greenhouse.db"):
        size = os.path.getsize("greenhouse.db")
        print(f"📁 Database file created: greenhouse.db ({size} bytes)")
