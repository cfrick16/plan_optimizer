from typing import List, Dict, Any
from pydantic import BaseModel


""" Model for the interval data csvs """


class IntervalDataPoint(BaseModel):
    datetime: str
    duration: int
    unit: str
    consumption: float
    generation: float
