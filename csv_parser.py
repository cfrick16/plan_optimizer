import pandas as pd
from io import StringIO
from fastapi import UploadFile
from typing import List
from models import IntervalDataPoint


async def parse_csv_file(file: UploadFile) -> List[IntervalDataPoint]:
    """Parse CSV from UploadFile - maximum speed optimizations"""
    contents = (await file.read()).decode("utf-8")

    # Ultra-fast pandas options
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

    # Use faster orient='records' directly
    return df.to_dict("records")
