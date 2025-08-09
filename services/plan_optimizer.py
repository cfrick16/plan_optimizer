from models import IntervalDataList, TariffConfig, PlanCostEvaluation
from typing import Dict, List
from collections import defaultdict


def get_total_cost_for_month(interval_data: IntervalDataList, tariff_config: TariffConfig) -> float:
    # 1. Add monthly fee 
    total_cost = tariff_config.monthly_fee

    # 2. Add usage cost
    for interval in interval_data:
        total_cost += interval.consumption * tariff_config.base_rate

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