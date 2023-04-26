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
