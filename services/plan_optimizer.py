from models import IntervalDataList, TariffConfig, PlanCostEvaluation
from typing import Dict, List
from collections import defaultdict
from models import IntervalDataPoint

'''
    Calculate the average rate for a given interval. 
    ex) if 2 minutes were charged at .1 and the final 1 minute was charged at .2, this would return .133

    Assumptions:
    - kwh_usage_rates never overlap within the tariff config.
    - kwh_usage_rates reset every month. (not clear from the requirements, but seems reasonable)
'''
def get_rate_for_interval(interval: IntervalDataPoint, wh_usage: float, tariff_config: TariffConfig) -> float:
    # 1. Initialize total rate and minutes touched
    total_rate = 0
    minutes_touched = 0

    # 2. Iterate over the kwh usage rate overrides, sum the rates for each minute and keep track of the number of minutes touched
    for kwh_usage_rate_override in tariff_config.kwh_usage_rate_overrides:
        override_min_wh = kwh_usage_rate_override.min_kwh * 1000
        override_max_wh = kwh_usage_rate_override.max_kwh * 1000
        if override_min_wh <= wh_usage <= override_max_wh:
            minutes_within_this_interval = min(interval.duration, override_max_wh - wh_usage)
            total_rate += kwh_usage_rate_override.rate * minutes_within_this_interval
            minutes_touched += minutes_within_this_interval

    # 3. Add the base rate for the remaining minutes
    total_rate += (interval.duration - minutes_touched) * tariff_config.base_rate
    return total_rate / interval.duration

def get_total_cost_for_month(interval_data: IntervalDataList, tariff_config: TariffConfig) -> float:
    # 1. Add monthly fee 
    total_cost = tariff_config.monthly_fee

    # 2. Iterate over the interval data
    wh_usage = 0
    for interval in interval_data:
        # 3. Calculate the cost for the interval
        total_cost += interval.consumption * get_rate_for_interval(interval, wh_usage, tariff_config)
        wh_usage += interval.consumption

    return total_cost

'''
    Calculate the average annual cost for a given tariff config and a given list of interval data.
    
    Assumptions: 
    - If there is a month with missing data for some time spans, it is assumed that no electricity was consumed/generated on those days.
'''
def calculate_plan_cost_evaluations(
    interval_data: IntervalDataList, tariff_config: TariffConfig
) -> PlanCostEvaluation:
    # 1. Group interval data by month
    interval_data_by_month = {}
    for interval in interval_data:
        year_month = f"{interval.datetime.year}-{interval.datetime.month}"
        if year_month not in interval_data_by_month:
            interval_data_by_month[year_month] = []
        interval_data_by_month[year_month].append(interval)


    # 2. Calculate total cost for each month
    total_cost = sum(map(lambda x: get_total_cost_for_month(x, tariff_config), interval_data_by_month.values()))

    # 3. Calculate average annual cost. Round to the nearest penny.
    num_years = len(interval_data) / 12
    avg_annual_cost = total_cost / num_years
    avg_annual_cost = round(avg_annual_cost, 2)

    return PlanCostEvaluation(
        tariff_config_id=tariff_config.id,
        tarrif_config_name=tariff_config.name,
        avg_annual_cost=avg_annual_cost
    )