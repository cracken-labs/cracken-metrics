import os

class Settings:
    VM_URL: str = os.getenv("VM_URL", "http://localhost:8428")
    GRAFANA_URL: str = os.getenv("GRAFANA_URL", "http://localhost:3000")
    # По умолчанию, если переменной нет (локальный дебаг без докера), упадем на sqlite, но в докере подхватим Postgres
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://cracken_admin:cracken_secure_pass@localhost:5432/cracken_control_plane"
    )

settings = Settings()
