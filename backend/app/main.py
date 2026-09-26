import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.promql_converter import PromQLConverter
from app.dashboard_generator import GrafanaDashboardGenerator
from app.moex_worker import moex_worker_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Фоновый воркер запускается строго при старте FastAPI
    worker_task = asyncio.create_task(moex_worker_loop())
    yield
    # И корректно тушится при остановке
    worker_task.cancel()

app = FastAPI(title="Cracken-Metrics API", lifespan=lifespan)
converter = PromQLConverter()
generator = GrafanaDashboardGenerator()

# Схема ожидаемых данных от фронтенда
class FormulaRequest(BaseModel):
    formula: str
    metric_name: str  # Название метрики, которое станет именем дашборда

@app.get("/")
def read_root():
    return {"status": "Cracken-Metrics Engine is running"}

@app.post("/api/convert")
async def convert_and_render_formula(request: FormulaRequest):
    try:
        # 1. Транслируем математику инвестора в синтаксис PromQL
        promql_result = converter.convert(request.formula)
        
        # 2. Делаем безопасный UID для Grafana (только буквы и цифры в нижнем регистре)
        safe_uid = "".join(c for c in request.metric_name if c.isalnum()).lower()
        if not safe_uid:
            safe_uid = "custom_dashboard_uid"
            
        # 3. Динамически создаем/обновляем дашборд внутри Grafana
        iframe_url = await generator.create_or_update_dashboard(
            uid=safe_uid,
            title=request.metric_name,
            promql_expression=promql_result
        )
        
        return {
            "success": True,
            "promql_expression": promql_result,
            "render_url": iframe_url  # Ссылка, которую фронтенд вставит в src iframe
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
