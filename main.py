from fastapi import FastAPI, File, UploadFile
from file_parser import parse_csv_interval_data, parse_json_tariff_config
from typing import List, Dict, Any

app = FastAPI()


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Hello World"}


@app.post("/recommend_plan")
async def recommend_plan(file: UploadFile = File(...)):
    interval_data = await parse_csv_interval_data(file)
    tariff_configs = await parse_json_tariff_config()

    return
