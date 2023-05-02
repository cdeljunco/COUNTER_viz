import pandas as pd
from datetime import datetime
import numpy as np
import streamlit as st
from typing import List

class TRJ1:
    """
    Represents a traditional TRJ1 file that includes the file and relevant data
    
    Parameters
    ----------
    name: str 
            Name of trj1 file
    dataframe: pd.DataFrame
            Pandas dataframe that was constructed from reading unedited TRJ1 file
    start_date: datetime, default None
            first date found in TRJ1 file
    end_date: datetime, default None
            last date found in TRJ1 file
    rpt: float, default None
            sum of reporting period total column
    cpu: float, default None
            cost per use, used for TRJ1's that are a complete FY
    projected_usage: int, default None
            projected usage calculated in helper_fxns.py and stored in var if current TRJ1 is not complete FY
    projected_cpu: float, default None
            projected cost per use given projected usage and cost, only used for incomplete FY TRj1's
    """

    def __init__(
        self,
        name: str, 
        dataframe: pd.DataFrame,
        start_date: datetime = None, 
        end_date: datetime = None,
        rpt: float = None, # reporting period total sum
        cpu: float = None,  # cost per use
        projected_usage: int = None, # projected usage to set cost per use
        projected_cpu: float = None # projected cost per use, set for not full fiscal years
    ) -> None:
        
        self.name = name
        self.dataframe = dataframe
        self.start_date = start_date
        self.end_date = end_date
        self.rpt = rpt # sum of unique or total item req
        self.cpu = cpu # cost per use
        self.projected_usage = projected_usage # projected usage to set cost per use
        self.projected_cpu = projected_cpu # projected cost per use, only set if not full fiscal year

    def __str__(self) -> str:
        list_data = ""
        for data in self.dataframe.columns.values:
            if type(data) == datetime:
                list_data += " " + data.strftime("%m/%Y")
            else:
                try:
                    new_datetime = pd.to_datetime(data)
                    list_data += " " + new_datetime.strftime("%m/%Y")
                except ValueError:
                    list_data += " " + data
        return self.name + list_data
    
    # Sets start date by iterating through headers and finding first datetime value
    def set_start_date(self) -> None:
        for header in self.dataframe.columns.values:
            if type(header) == datetime:
                self.start_date = header
                break

    # Sets end date by finding the last datetime header
    def set_end_date(self) -> None:
        for header in self.dataframe.columns.values:
            if type(header) == datetime:
                self.end_date = header

    # Sets rpt by summing the 'Reporting Period Total' column
    def set_reporting_period_total(self) -> None:
        self.rpt = self.dataframe['Reporting_Period_Total'].sum()
    
    # Sets cost per use given cost as a parameter
    def set_cost_per_use(self, cost) -> None:
        self.cpu = float(cost / self.rpt)

    def set_projected_usage(self, projection) -> None:
        self.projected_usage = projection

    def set_projected_cost_per_use(self, cost) -> None:
        self.projected_cpu = float(cost / self.projected_usage)

    # Determines whether file is a full Fiscal Year by subtracting start and end date
    def is_Full_FY(self) -> bool:
        diff = self.end_date - self.start_date # -> timedelta type
        return diff.days >= 335
    
    # Removes columns that will not be used 
    def clean_dataframe(self) -> None:
        self.set_start_date()
        self.set_end_date()
        self.dataframe.drop(columns=["Publisher", "Publisher_ID", "Platform",
             "DOI", "Proprietary_ID", "Print_ISSN", "Online_ISSN", "URI"], inplace=True)
        self.dataframe.replace(np.nan, 1, regex=True, inplace=True)
        self.dataframe = self.dataframe.rename_axis("Row Index")
    
    # Returns all dates as a list of datetime values
    def get_header_dates(self) -> List[datetime]:
        date_range = []
        for header in self.dataframe.columns.values:
            if type(header) == datetime:
                date_range.append(header)
            else:
                try:
                    timestamp_type = pd.to_datetime(header)
                    date_type = timestamp_type.date()
                    curr_datetime = datetime(date_type.year, date_type.month, date_type.day)
                    date_range.append(curr_datetime)
                except ValueError:
                    continue
        return date_range
