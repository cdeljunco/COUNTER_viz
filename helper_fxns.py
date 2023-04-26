from streamlit.runtime.uploaded_file_manager import UploadedFile
import pandas as pd
from trj1 import TRJ1
import streamlit as st
from typing import List
import os


# Read files uploaded based on file type
def read_file(file: UploadedFile, trj1_list: List[TRJ1]) -> pd.DataFrame:
    read_func = None
    if file.type == "text/csv":  # csv file
        read_func = pd.read_csv
    elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":  # xslx file
        read_func = pd.read_excel
    elif file.type == "text/tab-separated-values":  # tsv file
        read_func = lambda f, **kwargs: pd.read_csv(f, sep='\t', **kwargs)
    
    if not read_func:
        st.warning('Warning: Please upload a file of the correct type as listed above.', icon="⚠️")
        return pd.DataFrame()

    df = read_func(file, skiprows=13, index_col=False)
    trj1_file = TRJ1(file.name, df)
    trj1_file.clean_dataframe()
    trj1_list.append(trj1_file)

    return df

# Read default files at start of page/when no files are uploaded
def read_default_files(trj1_list: List[TRJ1]) -> pd.DataFrame:
    for file in os.listdir("./data"):
        df = pd.read_excel("./data/" + file,
                                skiprows=13,
                                index_col=False)  # use default data
        trj1_file = TRJ1(file, df)
        trj1_file.clean_dataframe()
        trj1_list.append(trj1_file)
    return df

# Metric choice is updated based on the radio option in app.py
def update_metric_choice(trj1_list: List[TRJ1], metric_choice: str) -> List[TRJ1]:
    metric_type = "Unique_Item_Requests" if metric_choice == "Unique Item Requests" else "Total_Item_Requests"
    for trj1 in trj1_list:
        trj1.dataframe = trj1.dataframe[trj1.dataframe["Metric_Type"] == metric_type].drop(columns=["Metric_Type"])
        trj1.set_reporting_period_total()
    return trj1_list

# Sort List of TRJ1 objects in chronological order
def sort_trj1_list(unsorted_trj1_list: List[TRJ1]) -> List[TRJ1]:
    return sorted(unsorted_trj1_list, key=lambda x: x.start_date)

# Checks if files have data for the same month, can be updated to say which files possibly
def check_duplicate_dates(trj1_list) -> None:
    all_dates = []
    dates_set = set()

    for trj1_file in trj1_list:
        all_dates.extend(trj1_file.get_header_dates())
        file_date_set = set(trj1_file.get_header_dates())
        dates_set = dates_set.union(file_date_set)

    if len(dates_set) != len(all_dates):
        st.warning('Warning: Two or more of your files contain data for the same month. \
                    To compare data across time periods, please upload non-ovelapping TR_J1 reports.',
                    icon="⚠️")

# If there exists a file with < 12 months of data, send warning once.
def check_fiscal_year(trj1_list):
    fiscal_warning_flag = False
    for trj1_file in trj1_list:
        if not trj1_file.is_Full_FY() and not fiscal_warning_flag:
            # st.write(trj1_file.name)  # can use this variable to identify which exact file
            st.warning('Warning: One of your files contains less than 12 months of data. Keep \
                            this in mind when calculating cost per use and comparing usage between \
                            years.', icon="⚠️")  # might give us multiple warnings
            fiscal_warning_flag = True