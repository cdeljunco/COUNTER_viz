import pandas as pd
import streamlit as st
import collections
from collections import defaultdict
import os
from trj1 import TRJ1
from streamlit.runtime.uploaded_file_manager import UploadedFile
import inflect
from typing import List
from figures import *

# intitializes inflect class for grammar
p = inflect.engine()
# Empty Panda Dataframe that stores a read TRJ1 File
df = pd.DataFrame()

# Empty List that holds TRJ1 Objects
trj1_list = []

# Saves the count of total TRJ1 Objects
trj1_count = 0

# Set the layout of the Streamlit
st.set_page_config(page_icon=None, page_title="Counter Visualization")

# Function to read file based on type
def read_file(file: UploadedFile) -> pd.DataFrame:
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

@st.cache_data
def read_default_files() -> pd.DataFrame:
    for file in os.listdir("./data"):
        df = pd.read_excel("./data/" + file,
                                skiprows=13,
                                index_col=False)  # use default data
        trj1_file = TRJ1(file, df)
        trj1_file.clean_dataframe()
        trj1_list.append(trj1_file)
    return df

def update_metric_choice(trj1_list: List[TRJ1], metric_choice: str) -> List[TRJ1]:
    metric_type = "Unique_Item_Requests" if metric_choice == "Unique Item Requests" else "Total_Item_Requests"
    for trj1 in trj1_list:
        trj1.dataframe = trj1.dataframe[trj1.dataframe["Metric_Type"] == metric_type].drop(columns=["Metric_Type"])
        trj1.set_reporting_period_total()
    return trj1_list


def sort_trj1_list(unsorted_trj1_list: List[TRJ1]) -> List[TRJ1]:
    return sorted(unsorted_trj1_list, key=lambda x: x.start_date)

# display sidebar
with st.sidebar:
    st.subheader(
        "The sidebar is resizable! Drag and drop the right border of the sidebar to resize it! ↔️")
    if file_upload := st.file_uploader(
        "Drag & drop or browse files to upload one unmodified TR-J1 spreadsheet per fiscal year:",
        type=['csv', 'tsv', 'xlsx'],
        accept_multiple_files=True,
    ):
        for file in file_upload:
            df = read_file(file)
        # displays files uploaded successfully using inflect module
        st.success(p.no("file", len(file_upload)) +
                            " uploaded successfully!", icon="✅")
    else:
        df = read_default_files()

trj1_count = len(trj1_list)
trj1_list = sort_trj1_list(trj1_list)

# Main image and header -- image will be removed
# image = Image.open('header.jfif')
# st.image(image)
st.markdown("#### This app analyzes and plots TR_J1 journal usage data to allow you \
            to easily assess the usage distribution, cost per use, and usage trends \
            over time for your library's journal package subscriptions.")

with st.expander("How to use:"):
    st.write("This app takes COUNTER 5 TR_J1 reports and subscription costs for a journal package and calculates the cost per use and journal usage distribution for the time periods covered by the TR-J1 reports. TR-J1 reports contain two usage metrics: Total_Item_Requests and Unique_Item_Requests. Most librarians use the Total_Item_Requests metric to evaluate usage, because it doesn't count repeat views and downloads of an item by the same user.")
    st.write(
        "To learn more about COUNTER 5 and TR_J1 metrics, visit: [the COUNTER website](https://www.projectcounter.org) or the [guide for librarians](https://www.projectcounter.org/wp-content/uploads/2018/03/Release5_Librarians_PDFX_20180307.pdf).")
    st.write(
        "This app was created by Rome Duong, Ricardo Zamora, and [Clara del Junco](https://cdeljunco.github.io/me/).")

# if there exists a file with < 12 months of data, send warning
for trj1_file in trj1_list:
    if not trj1_file.is_Full_FY():
        # st.write(trj1_file.name)  # can use this variable to identify which exact file
        st.warning('Warning: One of your files contains less than 12 months of data. Keep \
                        this in mind when calculating cost per use and comparing usage between \
                        years.', icon="⚠️")  # might give us multiple warnings


# Accurately gets all dates for each file and saves it to a dict using dict comprehension
# key = name of file, val = list of dates
df_dates = {trj1.name: trj1.get_header_dates() for trj1 in trj1_list}

# checks if files have data for the same month, can be updated to say which files possibly
all_dates = []
dates_set = set()

all_dates = [date for trj1_file in trj1_list for date in trj1_file.get_header_dates()]
dates_set = set(all_dates)

if len(dates_set) != len(all_dates):
    st.warning('Warning: Two or more of your files contain data for the same month. \
                To compare data across time periods, please upload non-ovelapping TR_J1 reports.',
                icon="⚠️")

st.write("#")  # simple spacer
st.write("#")  # simple spacer

# displays count of files uploaded using inflect module
st.subheader("You have successfully uploaded " + p.no("file",
                trj1_count) + " with the following details: ")

# extract unique item requests for each TRJ1 object in trj1_list
unique_journals = [trj1.dataframe['Metric_Type'].eq('Unique_Item_Requests').sum() for trj1 in trj1_list]
# create date column for display
date_col = [f"{date_range[0].strftime('%m/%Y')} - {date_range[-1].strftime('%m/%Y')}" for date_range in df_dates.values()]
# saving file data into one hashmap
file_details = {
    "File Name": list(df_dates),
    "Date Range": list(date_col),
    "Number of Journals": list(unique_journals),
}

# creates a collapsible view of the dataframe containing in details the reporting total, the titles, and the counts of journals
with st.expander("Expand to see file details:", expanded=True):
    # convert files' data into dataframe and display it, setting to max width
    file_details_df = pd.DataFrame(file_details)
    file_details_df = file_details_df.rename_axis("Row Index")
    st.dataframe(file_details_df, use_container_width=True)

st.write("#")  # simple spacer
# display tabs of dataframes in expander
with st.expander("Expand to see raw TR_J1 data:"):
    if not date_col:
        st.write("Please upload data")
    else:
        tabs = st.tabs(date_col)
        for i, trj1 in enumerate(trj1_list):
            with tabs[i]:
                st.dataframe(trj1.dataframe)


############### Streamlit radio for Metric Type ##############
st.write("#")  # simple spacer
#st.markdown("Learn more about <a href='https://www.projectcounter.org/about/'>COUNTER</a>.", unsafe_allow_html=True)
# https://medialibrary.projectcounter.org/file/The-Friendly-Guide-for-Librarians
# Decision Tree to verify that both metric types exist in trj1 files
if 'Unique_Item_Requests' in df['Metric_Type'].values and "Total_Item_Requests" in df['Metric_Type'].values:
    metric_choice = st.radio(
        "Select which metric type to use:",
        ("Unique Item Requests", "Total Item Requests")
    )
else:
    st.error(st.warning(
        'Please make sure that you have a valid metric type of Total Item Requests or Unique Item Requests', 
                icon="⚠️"))
# only include rows for specified metric choice
trj1_list = update_metric_choice(trj1_list, metric_choice)

# sidebar (Cost Per Use: Input and Output)
st.sidebar.write("#")  # simple spacer
st.sidebar.header("Cost Per Use")
st.sidebar.write(
    'Input the journal package cost in dollars for the period covered by each TR_J1 file:')
cpuDF = []
# cpuName = []
for i, trj1 in enumerate(trj1_list):
    cost = st.sidebar.number_input(
        ' ' + date_col[i] + ' ', min_value=0.00, format="%f", key=trj1.name)
    if cost != 0:
        trj1.set_cost_per_use(cost) 
    else: 
        trj1.cpu = 0
    st.sidebar.write("The Cost Per Use is : $ " + format(trj1.cpu, ".2f"))
    cpuDF.append(trj1.cpu)

############### Streamlit: Displaying Data #################
# using counter to get occurences of each num
titles_set = set()
max_df_values = []

title_header = "Journals with this many item requests(double-click to see full list)"
# loop through each dataframe in the list to create new dataframe
metric_choice = "Reporting_Period_Total"
count_header = "Number of journals with this many item requests"
title_header = "Titles of journals with this many item requests"

# Define a defaultdict to store the titles of the journals
titles = defaultdict(list)
titles_set = set()

# Iterate through the list of trj1 objects
occurrences_list = []

dfs = [trj1.dataframe for trj1 in trj1_list]

for df in dfs:
    # Count the number of occurrences of each value in the metric_choice column
    occurrences = df[metric_choice].value_counts().sort_index()
    # Group the data by the values in the metric_choice column
    grouped_data = df.groupby(metric_choice)
    # Apply a lambda function to each group to create a list of titles
    titles_list = grouped_data.apply(lambda x: x['Title'].tolist())
    # Combine the occurrences and titles_list into a single DataFrame
    usage_df = pd.concat([occurrences, titles_list], axis=1).reset_index()
    # Rename columns
    usage_df.columns = [metric_choice, count_header, title_header]
    # Store the titles in a defaultdict
    for index, row in usage_df.iterrows():
        titles[row[metric_choice]].extend(row[title_header])
        titles_set.update(row[title_header])
    occurrences_list.append(usage_df)

# Create Line plot of Distribution of Cost Per Use
st.header("Distribution of Cost Per Use")
if date_col and 0 not in cpuDF:
    fig1 = linePlot(date_col, cpuDF)[0]
    fig1.update_layout(yaxis=dict(range=[0, max(linePlot(date_col, cpuDF)[1]["Cost Per Use"])+1]))
    st.plotly_chart(fig1)
else:
    st.write("Please provide input for Cost Per Use")


# Usage Distribution - Tabs
st.write("#")  # simple spacer
st.header("Usage Distribution")
st.write("See which journals were used the most and least for each \
            of the time periods covered by your TR_J1 reports")
#st.caption("Click on each tab to view the specific Fiscal Year")
if not date_col:
    st.write("Please provide a data input")
else:
    hist_tab = st.tabs(date_col)
    # precompute max_report across all dataframes
    max_reports = [int(occurrences[metric_choice].max()) for occurrences in occurrences_list]
    # precompute the plural version of 'journal' for efficiency
    plural_journals = p.plural("journal", 2)
    for i, trj1 in enumerate(trj1_list):
        with hist_tab[i]:
            # get the dataframe from the list created earlier so it can be displayed
            usage_df = occurrences_list[i].rename_axis("Row Index")
            max_count = usage_df[count_header].max()

            # create a filter slider and use user input to create a filtered dataframe
            filter_slider = st.slider("Set the minimum and maximum reporting period total (x-axis) here.", 1, max_reports[i], value=(1, max_reports[i]))
            filtered_df = trj1.dataframe.query('Reporting_Period_Total >= @filter_slider[0] and Reporting_Period_Total <= @filter_slider[1]')

            # display number of filtered journals
            filter_count = len(filtered_df)
            filter_range = f"{filter_slider[0]} - {filter_slider[1]}" if filter_slider[0] != filter_slider[1] else f"{filter_slider[0]}"
            st.write(f"There {'is' if filter_count == 1 else 'are'} currently {p.no(plural_journals, filter_count)} within the following range: {filter_range} reporting period total")

            # determine the height for the histogram based on the maximum count
            chart_height = 600 if 300 <= max_count <= 600 else max_count if max_count < 300 else 500

            # create a collapsible view of the filtered dataframe
            with st.expander("Expand to see the filtered data behind the distribution:", expanded=False):
                st.write("#")
                st.caption("Click on column header to sort by ascending/descending order")
                st.dataframe(filtered_df, use_container_width=True)

            # display the histogram
            stacked_hist = histogram(filtered_df, filter_slider[1], chart_height)
            st.write("#")
            st.altair_chart(stacked_hist, use_container_width=True)

st.write("Click on plot and scroll to zoom, click & drag to move, \
            and double-click to reset view. Click ... at top right \
            to download the chart as an SVG/PNG.")

# Create a bar chart showing the reporting period for specific journals
st.header("Reporting Period Total over Time")
# multiselect option for titles
titles_selected = st.multiselect(
    "Search and click on the titles you want to view in the bar chart.",
    sorted(titles_set)
)  # contains a max selections param if we want the user to only select a limited amount

bar_df = []
bar_df.extend(titles_selected)

# determine whether the user has selected any journal
if not titles_selected:
    st.warning("To view journals over time, please select journals above.")
else:
    # create a new dataframe that combines all dataframes together and add a column of Fiscal Year to the dataframe corresponding to their fiscal year
    concat_df = pd.concat([df.dataframe.assign(Fiscal_Year=date_col[i]) for i, df in enumerate(trj1_list)], ignore_index=True)
    #st.dataframe(concat_df)
    if bar_df:
        # filter the dataframe by the selected titles
        df = concat_df[concat_df["Title"].isin(bar_df)]
        # convert the fiscal year column into a categorical variable and create a Plotly bar chart
        df['Fiscal_Year'] = pd.Categorical(df['Fiscal_Year'])
        fig = barChart(df)
        st.plotly_chart(fig)
    else:
        st.warning("Please select at least one title to view journals over time.")
