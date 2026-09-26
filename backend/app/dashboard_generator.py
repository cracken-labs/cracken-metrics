import httpx
import logging
from app.config import settings

logger = logging.getLogger("DashboardGenerator")

class GrafanaDashboardGenerator:
    def __init__(self):
        self.grafana_url = settings.GRAFANA_URL

    async def create_or_update_dashboard(self, uid: str, title: str, promql_expression: str) -> str:
        """
        Генерирует стандартный JSON-шаблон дашборда и отправляет его в API Grafana.
        Возвращает абсолютную ссылку для встраивания графика в iframe.
        """
        dashboard_json = {
            "dashboard": {
                "id": None,
                "uid": uid,
                "title": title,
                "tags": ["cracken-metrics"],
                "timezone": "browser",
                "schemaVersion": 38,
                "version": 1,
                "panels": [
                    {
                        "id": 1,
                        "type": "timeseries",
                        "title": f"Кастомная метрика: {title}",
                        "gridPos": {"h": 12, "w": 24, "x": 0, "y": 0}, # Растягиваем на весь экран
                        "targets": [
                            {
                                "datasource": {"type": "prometheus", "uid": "VictoriaMetrics"},
                                "expr": promql_expression, # Наш сгенерированный PromQL-запрос!
                                "legendFormat": "__auto",
                                "range": True
                            }
                        ],
                        "options": {
                            "legend": {"calcs": ["last", "min", "max"], "displayMode": "table", "placement": "bottom"}
                        },
                        "fieldConfig": {
                            "defaults": {
                                "custom": {"drawStyle": "line", "lineInterpolation": "smooth"},
                                "color": {"mode": "palette-classic"}
                            }
                        }
                    }
                ]
            },
            "overwrite": True
        }

        url = f"{self.grafana_url}/api/dashboards/db"
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.post(url, json=dashboard_json)
                if response.status_code == 200:
                    logger.info(f"Дашборд успешно создан в Grafana для UID: {uid}")
                    return f"http://localhost:3000/d/{uid}?orgId=1&kiosk=tv"
                else:
                    logger.error(f"Grafana API вернула ошибку {response.status_code}: {response.text}")
                    return ""
            except Exception as e:
                logger.error(f"Не удалось связаться с движком Grafana: {e}")
                return ""
