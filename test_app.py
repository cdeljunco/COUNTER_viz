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
from datetime import datetime
from projections import *

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
    if file.type == "text/csv":  # csv file
        df = pd.read_csv(file, skiprows=13, index_col=False)
    elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":  # xslx file
        df = pd.read_excel(file, skiprows=13)
    elif file.type == "text/tab-separated-values":  # tsv file
        df = pd.read_csv(file, sep='\t', skiprows=13)
    else:
        st.warning('Warning: Please upload a file of the correct type as listed above.',
                    icon="⚠️")
    trj1_file = TRJ1(file.name, df)
    trj1_file.clean_dataframe()
    trj1_list.append(trj1_file)
    return df


def read_default_files() -> pd.DataFrame:
    for file in os.listdir("./data"):
        df = pd.read_excel("./data/" + file,
                                skiprows=13,
                                index_col=False)  # use default data
        trj1_file = TRJ1(file, df)
        trj1_file.clean_dataframe()
        trj1_list.append(trj1_file)
    return df


def update_metric_choice(trj1_list: List[TRJ1], metric_choice: str):
    metric_trj1_list = trj1_list
    for trj1 in metric_trj1_list:
        if metric_choice == "Unique Item Requests":
            trj1.dataframe = trj1.dataframe.loc[trj1.dataframe['Metric_Type']
                                                == "Unique_Item_Requests"]
        else:
            trj1.dataframe = trj1.dataframe.loc[trj1.dataframe['Metric_Type']
                                                == "Total_Item_Requests"]
        trj1.dataframe.drop(columns="Metric_Type", inplace=True)
        trj1.set_reporting_period_total()
    return metric_trj1_list

def sort_trj1_list(unsorted_trj1_list: List[TRJ1]) -> List[TRJ1]:
    return sorted(unsorted_trj1_list, key=lambda x: x.start_date)

# display sidebar
with st.sidebar:
    st.subheader(
        "The sidebar is resizable! Drag and drop the right border of the sidebar to resize it! ↔️")
    # Upload file - of type csv, tsv, or xlsx (read excel can also accept xls, xlsx, xlsm, xlsb, odf, ods and odt)
    file_upload = st.file_uploader("Drag & drop or browse files to upload one unmodified TR-J1 spreadsheet per fiscal year:",
                                        type=['csv', 'tsv', 'xlsx'],
                                        accept_multiple_files=True)
    # Decision Tree to upload the files
    if file_upload:
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

for trj1_file in trj1_list:
    all_dates.extend(trj1_file.get_header_dates())
    file_date_set = set(trj1_file.get_header_dates())
    dates_set = dates_set.union(file_date_set)

if len(dates_set) != len(all_dates):
    st.warning('Warning: Two or more of your files contain data for the same month. \
                To compare data across time periods, please upload non-ovelapping TR_J1 reports.',
                icon="⚠️")

st.write("#")  # simple spacer
st.write("#")  # simple spacer

# displays count of files uploaded using inflect module
st.subheader("You have successfully uploaded " + p.no("file",
                trj1_count) + " with the following details: ")

# Identify Unique Journals per TRJ1 file by counting len of unique item requests
unique_journals = []
for trj1 in trj1_list:
    unique_journals.append(
        len(trj1.dataframe.loc[trj1.dataframe['Metric_Type']
            == 'Unique_Item_Requests'])
    )

# listing dates based off either it is date time class or string
date_col = []
for date_range in df_dates.values():
    date_col.append(date_range[0].strftime(
        "%m/%Y") + " - " + date_range[-1].strftime("%m/%Y"))

# saving file data into one hashmap
file_details = {
    "File Name": [file for file in df_dates],
    "Date Range": [date for date in date_col],
    "Number of Journals": [num for num in unique_journals]
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
    trj1.set_cost_per_use(cost)
    st.sidebar.write("The Cost Per Use is : $ " + format(trj1.cpu, ".2f"))
    cpuDF.append(trj1.cpu)
    # cpuName.append(trj1.name)

############### Streamlit: Displaying Data #################
# using counter to get occurences of each num
occurrences_list = []
titles_set = set()
max_df_values = []

# loop through each dataframe in the list to create new dataframe
for trj1 in trj1_list:
    df = trj1.dataframe
    occurrences = collections.Counter(df["Reporting_Period_Total"])
    titles = defaultdict(list)
    # There must be at least one journal linked to rpt, thus we can use a defaultdict and assure that there are no empty lists
    for index, row in df.iterrows():
        titles[row["Reporting_Period_Total"]].append(row['Title'])
        titles_set.add(row['Title'])

    # create a dictionary that would contain the count numbers, the reporting total, and the titles of the journals
    count_header = "Number of journals with this many item requests"
    title_header = "Journals with this many item requests(double-click to see full list)"
    data = {
        metric_choice: [key for key, _ in occurrences.items()],
        count_header: [val for _, val in occurrences.items()],
        title_header: [val for _, val in titles.items()]
    }
    usage_df = pd.DataFrame(data)
    # max_df_values.append(usage_df[metric_choice].max())
    occurrences_list.append(usage_df)

# Create Line plot of Distribution of Cost Per Use
st.header("Distribution of Cost Per Use")
fig1 = linePlot(date_col, cpuDF)[0]
fig1.update_layout(yaxis=dict(range=[0, max(linePlot(date_col, cpuDF)[1]["Cost Per Use"])+1]))
st.plotly_chart(fig1)


# Usage Distribution - Tabs
st.write("#")  # simple spacer
st.header("Usage Distribution")
st.write("See which journals were used the most and least for each \
            of the time periods covered by your TR_J1 reports")
#st.caption("Click on each tab to view the specific Fiscal Year")
hist_tab = st.tabs(date_col)
for i, trj1 in enumerate(trj1_list):
    with hist_tab[i]:
        # create a dataframe from the dictionary created earlier so it could be later be dsiplayed or performed with other python functions
        # determine the maximum numbers to better scale the x-axis(max_report) and y-axis(max_count)
        usage_df = occurrences_list[i]
        usage_df = usage_df.rename_axis("Row Index")
        max_count = usage_df[count_header].max()
        max_report = int(usage_df[metric_choice].max())
        chartHeight = 0
        stacked_df = trj1.dataframe

        # create a filter silder and use user input to create a filtered dataframe
        filter_slider = st.slider("Set the minimum and maximum reporting period total (x-axis) here.",
                                    1, max_report,
                                    value=(1, max_report))  # slider for user to check a varying range of reporting period totals
        filter_min = filter_slider[0]
        filter_max = filter_slider[1]
        filter_diff = filter_max - filter_min
        filter = stacked_df["Reporting_Period_Total"].between(
            filter_min, filter_max, "both")  # returns whether element in Series is between
        # creates a filtered dataframe by only including elements that are true from filter variable
        filtered_df = stacked_df[filter]
        filter_count = len(filtered_df)

        # grammar based on filter slider using inflect
        if filter_diff:
            st.write("There " + p.plural("is", filter_count) + " currently " + p.no("journal", filter_count) +
                    " within the following range: {} - {} reporting period total".format(filter_min, filter_max))
        else:
            st.write("There " + p.plural("is", filter_count) + " currently " + p.no(
                "journal", filter_count) + " with {} reporting period total".format(filter_min))

        # condition to determine the height for the histogram
        if max_count >= 300:
            if max_count >= 300 & max_count <= 600:
                chartHeight = 600
            else:
                chartHeight = max_count
        else:
            chartHeight = 500

        # creates a collapsible view of the dataframe containing in details the reporting total, the titles, and the counts of journals
        with st.expander("Expand to see the filtered data behind the distribution:", expanded=False):
            st.write("#")  # spacing between text
            st.caption(
                "Click on column header to sort by ascending/descending order")
            st.dataframe(filtered_df, use_container_width=True)

        stacked_hist = histogram(filtered_df, filter_max, chartHeight)
        st.write("#")  # simple spacer
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
    st.warning(
        "To view journals over time, please select journals above.")
else:
    # add a column of Fiscal Year to the dataframe corresponding to their fiscal year
    for i in range(len(trj1_list)):
        df = trj1_list[i].dataframe
        df = df.iloc[:, [0, 1]]
        df["Fiscal Year"] = date_col[i]
        trj1_list[i].dataframe = df

    # create a new dataframe that bind all of the dataframes together
    concat_df = pd.concat([df.dataframe for df in trj1_list])
    df = ""
    if bar_df != "":
        # create a dataframe that will only contain the titles of the journals that the user selected
        df = concat_df[concat_df["Title"].isin(bar_df)]
    st.dataframe(df, use_container_width=True)

    # convert the fiscal year column into a categorical variable
    df['Fiscal Year'] = df['Fiscal Year'].astype('category')
    #create a Plotly barchart
    fig = barChart(df)
    st.plotly_chart(fig)
    st.write("Please keep in mind that perhaps not all journals may be present in every file, therefore certain journals may not have a full collection of bars in the graph above.")
### TEST ###





complete_trj1_list, incomplete_trj1 = set_complete_incomplete_files(trj1_list)

# test_trj1 = complete_trj1_list[0] # TO DELETE
# st.write([trj1.name for trj1 in complete_trj1_list])
# st.write(incomplete_trj1)
# count of months in incomplete trj1
# months_completed = diff_month(incomplete_trj1)

# usage = usage_up_to_month(months_completed, test_trj1.dataframe)



# fraction = fraction_of_total_uses(usage, test_trj1.rpt)




projection = project_total_uses(complete_trj1_list, incomplete_trj1)
st.write(projection)
st.write([trj1.rpt for trj1 in trj1_list])



remaining_months = calculate_remaining_months(incomplete_trj1)
st.write(remaining_months)




# #4 might be useless
# def total_usage_up_to_month(total_usage, fraction):
#     return total_usage * fraction

# total_usage_to_x = total_usage_up_to_month(test_trj1.rpt, fraction)



# with st.expander("test", expanded=False):
#     st.write(usage)
#     st.write(fraction)
#     st.write(total_usage_to_x)


# headers = complete_trj1_list[0].dataframe.columns.values.tolist()

# incomplete_trj1.get_header_dates()
# data.strftime("%m/%Y")
# st.write(complete_trj1_list[0].dataframe.columns.values.tolist())
# st.write(incomplete_trj1.end_date)
# st.write(complete_trj1_list)
# st.write(incomplete_trj1)
# st.write(trj1.dataframe)


# use .month on datetime to get month
# st.write(incomplete_trj1.end_date.month)