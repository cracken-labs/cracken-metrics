from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.promql_converter import PromQLConverter

app = FastAPI(title="Cracken-Metrics API")
converter = PromQLConverter()

# Схема входных данных от пользователя
class FormulaRequest(BaseModel):
    formula: str

@app.get("/")
def read_root():
    return {"status": "Cracken-Metrics Engine is running"}

@app.post("/api/convert")
def convert_formula(request: FormulaRequest):
    try:
        promql_result = converter.convert(request.formula)
        return {
            "success": True,
            "origin_formula": request.formula,
            "promql_expression": promql_result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
