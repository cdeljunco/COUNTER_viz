# This file contains all of the functions that calculate the projected usage
# for a TRJ1 with an incomplete Fiscal Year

from datetime import datetime
import pandas as pd
from typing import List, Tuple
from trj1 import TRJ1

# Identify complete files and the single incomplete trj1
def set_complete_incomplete_files(trj1_list: List[TRJ1]) -> Tuple[List[TRJ1], List[TRJ1]]:
    # List TRJ1 with full Fiscal Year
    complete_trj1_list = []
    
    # List TRJ1 with incomplete Fiscal Year
    incomplete_trj1 = []

    for trj1 in trj1_list:
        if trj1.is_Full_FY():
            complete_trj1_list.append(trj1)
        else:
            incomplete_trj1.append(trj1)

    return (complete_trj1_list, incomplete_trj1)

# TOTAL USAGE: over the course of the year is simply <trj1.rpt> -- #1
# Returns the count of months from end_date to start_date
def diff_month(trj1: TRJ1) -> int:
    return (trj1.end_date.year - trj1.start_date.year) * 12 + trj1.end_date.month - trj1.start_date.month + 1 # +1 for the offset

# Find usage up to month x -- #2 (this will be used)
def usage_up_to_month(month: int, df: pd.DataFrame) -> int:
    usage = 0
    month_count = 0

    for columnName, columnData in df.items():
        if type(columnName) == datetime:
            if month_count < month:
                usage += columnData.values.sum()
                # st.write(columnName.strftime("%m/%Y"))
                # st.write((columnData.values.sum()))
                month_count += 1
            # else:
                # ttt = columnName.strftime("%m/%Y")
                # st.write("Not Calculated: ", columnName.strftime("%m/%Y"))
            # if month_count >= months_completed:
            #     st.write(columnName.strftime("%m/%Y"))
            #     st.write((columnData.values.sum()))
            # else:
            #     month_count += 1
    return usage

# params: (usage up to month, rpt--total usage)
def fraction_of_total_uses(usage: int, total_usage: int) -> float:
    # can round up to nearest nth
    # print(round(x))    		#output: 6
    # print(round(x, 3)) 		#output: 6.346
    # print(round(x, 1)  		#output: 6.3
    return usage / total_usage
# Calculates projected usage for the given incomplete FY TRJ1, given List of complete TRJ1's
def project_total_uses(complete_trj1_list: List, incomplete_trj1: TRJ1) -> int:
    fraction = 0.0
    months_completed = diff_month(incomplete_trj1)

    for trj1 in complete_trj1_list:
        usage = usage_up_to_month(months_completed, trj1.dataframe)
        fraction += fraction_of_total_uses(usage, trj1.rpt)

    average_fraction = fraction/len(complete_trj1_list)
    projected_total = round(incomplete_trj1.rpt / average_fraction)

    return projected_total

# Function can be used to display to user which months are missing within the Fiscal Year
def calculate_remaining_months(incomplete_trj1: TRJ1) -> List[str]:
    # Create a list to save the projections missing 
    remaining_months = []
    month = incomplete_trj1.end_date.month
    year = incomplete_trj1.end_date.year

    while month < 6:
        if month <= 12:
            month += 1
        else:
            month = 1
            year += 1

        remaining_months.append(f"{month}/{year}")

    return remaining_months
