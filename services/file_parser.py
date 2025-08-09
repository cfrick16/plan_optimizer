import pandas as pd
import json
from io import StringIO
from fastapi import UploadFile
from models import IntervalDataList, TariffConfigList, TariffConfig, IntervalDataPoint


async def parse_json_tariff_config() -> TariffConfigList:
    # From a file
    with open('tariff_config.json', 'r') as f:
        data = json.load(f)

    tariff_configs = []
    for tariff_data in data['tariffs']:
        tariff_configs.append(TariffConfig(**tariff_data))
    
    return tariff_configs


async def parse_csv_interval_data(file: UploadFile) -> IntervalDataList:
    contents = (await file.read()).decode("utf-8")

    df = pd.read_csv(
        StringIO(contents),
        parse_dates=['datetime'],
        dtype={
            "duration": int,
            "unit": str,
            "consumption": float,
            "generation": float,
        },
    )

    interval_data_list = []
    for interval_data_point in df.to_dict("records"):
        interval_data_list.append(IntervalDataPoint(**interval_data_point))
    return interval_data_list
