from typing import List, Dict, Any
from pydantic import BaseModel


""" Model for the interval data csvs """
class IntervalDataPoint(BaseModel):
    datetime: str
    duration: int
    unit: str
    consumption: float
    generation: float

IntervalDataList = List[IntervalDataPoint]


""" Models for the tariff config json """
class KwhUsageRateOverride(BaseModel):
    min_kwh: float
    max_kwh: float
    rate: float

class TimeBasedRateOverride(BaseModel):
    start_time: str
    end_time: str
    rate: float

class TariffConfig(BaseModel):
    id: int
    name: str
    monthly_fee: float
    base_rate: float
    kwh_usage_rate_overrides: List[KwhUsageRateOverride]
    time_based_rate_overrides: List[TimeBasedRateOverride] 

TariffConfigList = List[TariffConfig]
