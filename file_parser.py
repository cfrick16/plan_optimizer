import pandas as pd
import json
from io import StringIO
from fastapi import UploadFile
from models import IntervalDataList, TariffConfigList, TariffConfig


async def parse_json_tariff_config() -> TariffConfigList:
    # From a file
    with open('tariff_config.json', 'r') as f:
        data = json.load(f)


    return  data['tariffs']


async def parse_csv_interval_data(file: UploadFile) -> IntervalDataList:
    contents = (await file.read()).decode("utf-8")

    df = pd.read_csv(
        StringIO(contents),
        dtype={
            "datetime": str,
            "duration": int,
            "unit": str,
            "consumption": float,
            "generation": float,
        },
    )

    return df.to_dict("records")
