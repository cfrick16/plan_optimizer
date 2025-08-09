from fastapi import FastAPI, File, UploadFile
from services.file_parser import parse_csv_interval_data, parse_json_tariff_config
from typing import List, Dict, Any
from models import RecommendPlanResult
from services.plan_optimizer import calculate_plan_cost_evaluations

app = FastAPI()

@app.post("/recommend_plan")
async def recommend_plan(file: UploadFile = File(...)) -> RecommendPlanResult:
    interval_data = await parse_csv_interval_data(file)
    tariff_configs = await parse_json_tariff_config()

    plan_cost_evaluations = list(map(
        lambda t: calculate_plan_cost_evaluations(interval_data, t), tariff_configs
    ))

    return sorted(plan_cost_evaluations, key=lambda x: x.avg_annual_cost)
