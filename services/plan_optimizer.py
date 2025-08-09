from models import IntervalDataList, TariffConfig, PlanCostEvaluation
from typing import Dict, List
from collections import defaultdict
from models import IntervalDataPoint
from services.date_time_helper import is_time_in_range

'''
    Calculate the average rate for a given interval. 
    ex) if 2 minutes were charged at .1 and the final 1 minute was charged at .2, this would return .133

    Assumptions:
    - Time based rate overrides are applied the same for the entire entry interval based on the start time since it's impossible to know the exact time of the day.
    - kwh_usage_rates never overlap within the tariff config.
    - kwh_usage_rates reset every month. (not clear from the requirements, but seems reasonable)
    - If there is a valid time and kwh useage rate override, the lower rate is applied.
'''
def get_rate_for_interval(interval: IntervalDataPoint, total_wh_usage: float, tariff_config: TariffConfig, wh_to_buy: float) -> float:
    # 1. Initialize total rate and watt hours touched
    total_rate = 0
    wh_covered = 0
    time_based_rate = None

    # 2. Find any time based rate overrides that apply to this interval
    time_based_rate_overrides = []
    for time_based_rate_override in tariff_config.time_based_rate_overrides:
        if is_time_in_range(interval.datetime, time_based_rate_override.start_time, time_based_rate_override.end_time):
            time_based_rate = time_based_rate_override.rate

    # 3. Iterate over the kwh usage rate overrides, sum the rates for each minute and keep track of the number of minutes touched
    for kwh_usage_rate_override in tariff_config.kwh_usage_rate_overrides:
        override_min_wh = kwh_usage_rate_override.min_kwh * 1000
        override_max_wh = kwh_usage_rate_override.max_kwh * 1000
        if override_min_wh <= total_wh_usage <= override_max_wh:
            # Ignore the kwh useage rate override if the time based rate is lower
            if time_based_rate is None or time_based_rate > kwh_usage_rate_override.rate:
                wh_within_this_interval = min(wh_to_buy, override_max_wh - total_wh_usage)
                total_rate += kwh_usage_rate_override.rate * wh_within_this_interval
                wh_covered += wh_within_this_interval

    # 4. Determine what the rate should be for the remaining watt hours
    base_rate = time_based_rate if time_based_rate is not None else tariff_config.base_rate

    # 5. Add the base rate for the remaining whs used
    total_rate += (wh_to_buy - wh_covered) * base_rate
    return total_rate / interval.duration

def get_total_cost_for_month(interval_data: IntervalDataList, tariff_config: TariffConfig, rollover_wh: float) -> float:
    # 1. Add monthly fee 
    total_cost = tariff_config.monthly_fee
    current_rollover_wh = rollover_wh

    # 2. Iterate over the interval data
    total_wh_usage = 0
    for interval in interval_data:
        # 3. Use any leftover rollover_wh before calculating the cost for the interval
        wh_to_buy = max(interval.consumption - current_rollover_wh, 0)
        current_rollover_wh = max(current_rollover_wh - wh_to_buy, 0)

        # 4. Calculate the cost for the interval
        total_cost += wh_to_buy / 1000 * get_rate_for_interval(interval, total_wh_usage, tariff_config, wh_to_buy)
        total_wh_usage += wh_to_buy

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
    total_cost = sum(map(lambda x: get_total_cost_for_month(x, tariff_config, 0), interval_data_by_month.values()))

    # 3. Calculate average annual cost. Round to the nearest penny.
    num_years = len(interval_data_by_month) / 12
    avg_annual_cost = total_cost / num_years
    avg_annual_cost = round(avg_annual_cost, 2)

    return PlanCostEvaluation(
        tariff_config_id=tariff_config.id,
        tarrif_config_name=tariff_config.name,
        avg_annual_cost=avg_annual_cost,
        total_cost=total_cost
    )