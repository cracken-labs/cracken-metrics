import os

class Settings:
    VM_URL: str = os.getenv("VM_URL", "http://localhost:8428")
    GRAFANA_URL: str = os.getenv("GRAFANA_URL", "http://localhost:3000")

settings = Settings()
