import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import collections
import random
from collections import defaultdict
from PIL import Image
from datetime import datetime
import os
import time
from trj1 import TRJ1

# Create a variable to represent an empty Panda Dataframe, create an empty list to hold list of DataFrames
df = pd.DataFrame()
list_df = []
file_names = []
file_count = 0

trj1_list = []
trj1_count = 0

# Set the layout of the Streamlit
st.set_page_config(page_icon=None,
                   page_title="Counter Visualization")

# display sidebar
with st.sidebar:
    st.subheader("The sidebar is resizable! Drag and drop the right border of the sidebar to resize it! ↔️")
    # Upload file - of type csv, tsv, or xlsx (read excel can also accept xls, xlsx, xlsm, xlsb, odf, ods and odt)
    file_upload = st.file_uploader("Drag & drop or browse files to upload one unmodified TR-J1 spreadsheet per fiscal year:",
                                type=['csv', 'tsv', 'xlsx'], accept_multiple_files=True)
    # Decision Tree to upload the files
    if file_upload:
        file_count = len(file_upload)
        trj1_count = len(file_upload)
        for file in file_upload:
            if file.type == "text/csv":  #csv file
                df = pd.read_csv(file, skiprows=13, index_col=False)
            elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":  # xslx file
                df = pd.read_excel(file, skiprows=13)
            elif file.type == "text/tab-separated-values":  # tsv file
                df = pd.read_csv(file, sep='\t', skiprows=13)
            else:
                st.warning(
                    'Warning: Please upload a file of the correct type as listed above.', icon="⚠️")
            list_df.append(df)
            file_names.append(file.name)

            trj1_file = TRJ1(file.name, df)
            trj1_file.clean_dataframe()
            trj1_list.append(trj1_file)

        # wording based on files uploaded
        if trj1_count > 1:
            st.success(str(trj1_count) + " files uploaded successfully!", icon="✅")
        elif trj1_count == 1:
            st.success("File uploaded successfully!", icon="✅")
    else:
        for file in os.listdir("./data"):
            df = pd.read_excel("./data/" + file, skiprows=13,
                            index_col=False)  # use default data
            list_df.append(df)
            file_names.append(file)

            trj1_file = TRJ1(file, df)
            trj1_file.clean_dataframe()
            trj1_list.append(trj1_file)

        file_count = len(list_df)
        trj1_count = len(trj1_list)

# Main image and header -- image will be removed
# image = Image.open('header.jfif')
# st.image(image)
st.markdown("#### This app analyzes and plots TR_J1 journal usage data to allow you to easily assess the usage distribution, cost per use, and usage trends over time for your library's journal package subscriptions.")

with st.expander("How to use:"):
    st.write("This app takes COUNTER 5 TR_J1 reports and subscription costs for a journal package and calculates the cost per use and journal usage distribution for the time periods covered by the TR-J1 reports. TR-J1 reports contain two usage metrics: Total_Item_Requests and Unique_Item_Requests. Most librarians use the Total_Item_Requests metric to evaluate usage, because it doesn't count repeat views and downloads of an item by the same user.")
    st.write(
        "To learn more about COUNTER 5 and TR_J1 metrics, visit: [the COUNTER website](https://www.projectcounter.org) or the [guide for librarians](https://www.projectcounter.org/wp-content/uploads/2018/03/Release5_Librarians_PDFX_20180307.pdf).")
    st.write(
        "This app was created by Rome Duong, Ricardo Zamora, and [Clara del Junco](https://cdeljunco.github.io/me/).")

# cleaning data by dropping unecessary rows and coverting NaN types to 0
# df = df.drop(columns=["Publisher", "Publisher_ID", "Platform",
#              "DOI", "Proprietary_ID", "Print_ISSN", "Online_ISSN", "URI"])
# for i, df_clean in enumerate(list_df):
#     df_clean.drop(columns=["Publisher", "Publisher_ID", "Platform",
#                              "DOI", "Proprietary_ID", "Print_ISSN", "Online_ISSN", "URI"], inplace=True)
#     df_clean.replace(df.replace(np.nan, 1, regex=True, inplace=True))
#     df_clean = df_clean.rename_axis("Row Index")
#     list_df[i] = df_clean


# df.replace(np.nan, 1, regex=True, inplace=True)
# st.write("caca")
# for file in trj1_list:
#     st.write(file.name)




for trj1_file in trj1_list:
    if not trj1_file.is_Full_FY():
        # st.write(trj1_file.name)  # can use this variable to identify which exact file
        st.warning('Warning: One of your files contains less than 12 months of data. Keep \
                   this in mind when calculating cost per use and comparing usage between \
                   years.', icon="⚠️")

# Accurately gets all dates for each file and saves it to a dict
# key = name of file, val = list of dates
# df_dates = {}
# for i, given_df in enumerate(list_df):
#     # st.write(given_df)
#     col_names = list(given_df.columns)[3:]

#     # if len(col_names) < 12:
#     #     st.warning('Warning: One of your files contains less than 12 months of data. Keep this in mind when calculating cost per use and comparing usage between years.', icon="⚠️")
#     df_dates[file_names[i]] = col_names # file_names[i] = name of file "SpringerLink-TR_J1-FY22.xlsx" , col names is list of date_time types
#     # st.write(type(file_names[i]))
#     # st.write(file_names[i])
#     # st.write(type(col_names))
#     # st.write(col_names)

df_dates = {}

for trj1_file in trj1_list:
    df_dates[trj1_file.name] = trj1_file.get_header_dates()


# checks if files have data for the same month, can be updated to say which files possibly


# distinct_dates = []
# for file, date_range in df_dates.items():
#     for date in date_range:
#         if date in distinct_dates:
#             st.warning('Warning: Two or more of your files contain data for the same month. To compare data across time periods, please upload non-ovelapping TR_J1 reports.', icon="⚠️")

#         else:
#             distinct_dates.append(date)
# checks if files have the same month, displays warning message
all_dates = []
dates_set = set()

for trj1_file in trj1_list:
    all_dates.extend(trj1_file.get_header_dates())
    file_date_set = set(trj1_file.get_header_dates())
    dates_set = dates_set.union(file_date_set)
    
if len(dates_set) != len(all_dates):
    st.warning('Warning: Two or more of your files contain data for the same month. To compare data across time periods, please upload non-ovelapping TR_J1 reports.', icon="⚠️")



st.write("#")  # simple spacer
st.write("#")  # simple spacer

# wording based on number of files uploaded
if trj1_count > 1:
    st.subheader("You have successfully uploaded " +
                 str(trj1_count) + " files with the following details:")
elif trj1_count == 1:
    st.subheader(
        "You have successfully uploaded a file with the following details:")


# Identify Unique Journals per TRJ1 file
unique_journals = []
for trj1 in trj1_list:
    unique_journals.append(
            len(trj1.dataframe.loc[trj1.dataframe['Metric_Type'] == 'Unique_Item_Requests']))

# for given_df in list_df:
#     unique_journals.append(
#         len(given_df.loc[given_df['Metric_Type'] == 'Unique_Item_Requests']))

# listing dates based off either it is date time class or string
date_col = []
for date_range in df_dates.values():
    date_col.append(date_range[0].strftime(
        "%m/%Y") + " - " + date_range[-1].strftime("%m/%Y"))

# saving file data into one hashmap
file_details = {
    "File Name": [file_name for file_name in df_dates],
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
#st.subheader("View More File Details")
with st.expander("Expand to see raw TR_J1 data:"):
    tabs = st.tabs(date_col)
    for i, trj1 in enumerate(trj1_list):
        with tabs[i]:
            st.dataframe(trj1.dataframe)


############### Streamlit radio for Metric Type ##############
st.write("#")  # simple spacer
#st.markdown("Learn more about <a href='https://www.projectcounter.org/about/'>COUNTER</a>.", unsafe_allow_html=True)
# https://medialibrary.projectcounter.org/file/The-Friendly-Guide-for-Librarians
# Decision Tree for whether there exists more than one metric type on file
if 'Unique_Item_Requests' in df['Metric_Type'].values and "Total_Item_Requests" in df['Metric_Type'].values:
    metric_choice = st.radio(
        "Select which metric type to use:",
        ("Unique Item Requests", "Total Item Requests")
    )
else:
    st.error(st.warning(
        'Please make sure that you have a valid metric type of Total Item Requests or Unique Item Requests', icon="⚠️"))

for trj1 in trj1_list:
    if metric_choice == "Unique Item Requests":
        trj1.dataframe = trj1.dataframe.loc[trj1.dataframe['Metric_Type'] == "Unique_Item_Requests"]
    else:
        trj1.dataframe = trj1.dataframe.loc[trj1.dataframe['Metric_Type'] == "Total_Item_Requests"]
    trj1.dataframe.drop(columns = "Metric_Type", inplace = True)
    trj1.set_reporting_period_total()



# if metric_choice == "Unique Item Requests":
#     for trj1 in trj1_list:
#         trj1.dataframe = trj1.dataframe.loc[trj1.dataframe['Metric_Type'] == "Unique_Item_Requests"]
#         trj1.dataframe.drop(columns = "Metric_Type", inplace = True)
#     # for i, df_choice in enumerate(list_df):
#     #     df_choice = df_choice.loc[df_choice['Metric_Type']
#     #                               == "Unique_Item_Requests"]
#     #     df_choice = df_choice.drop(columns="Metric_Type")
#     #     list_df[i] = df_choice

# else:
#     for trj1 in trj1_list:
#         trj1.dataframe = trj1.dataframe.loc[trj1.dataframe['Metric_Type'] == "Total_Item_Requests"]
#         trj1.dataframe.drop(columns = "Metric_Type", inplace = True)


    # for i, df_choice in enumerate(list_df):
    #     df_choice = df_choice.loc[df_choice['Metric_Type']
    #                               == "Total_Item_Requests"]
    #     df_choice = df_choice.drop(columns="Metric_Type")
    #     list_df[i] = df_choice

# Determine the report total based on whether "Total Unique Item Requests" exist in the "Title" column

# sum reporting period total column
# rpt_list = []

# for df_rpt in list_df:
#     rpt = df_rpt['Reporting_Period_Total'].sum()
#     rpt_list.append(rpt)

# # cost input, shows warning alert if no input, else success alert and display cost per report
# st.sidebar.write("#")  # simple spacer
# st.sidebar.header("Cost Per Use")
# st.sidebar.write('Input the journal package cost in dollars for the period covered by each TR_J1 file:',)
# cost_per_file = []
# for i, df in enumerate(list_df):
#     cost = st.sidebar.number_input(
#         ' ' + file_names[i] + ' ', min_value=0.00, format="%f", key=file_names[i])
#     cost_per_file.append(cost)

st.sidebar.write("#")  # simple spacer
st.sidebar.header("Cost Per Use")
st.sidebar.write('Input the journal package cost in dollars for the period covered by each TR_J1 file:')
for trj1 in trj1_list:
    cost = st.sidebar.number_input(' ' + trj1.name + ' ', min_value=0.00, format="%f", key=trj1.name)
    trj1.set_cost_per_use(cost)

st.sidebar.subheader("Based on your input, the cost per use for...")

for i, trj1 in enumerate(trj1_list):    
    st.sidebar.write(date_col[i] + " is : $ " + format(trj1.cpu, ".2f"))



# cpt_list = []
# st.sidebar.subheader("Based on your input, the cost per use for...")
# for i, val in enumerate(rpt_list):
#     cpt = format(cost_per_file[i]/rpt_list[i], ".2f")
#     cpt_list.append(cpt)
#     st.sidebar.write(date_col[i] + " is : $ " + cpt)


# ############### Streamlit: Displaying Data #################
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


st.sidebar.write("#") # simple spacer

# multiselect option for titles
titles_selected = st.sidebar.multiselect(
    "Click on the titles you want to view on the chart",
    titles_set
) # contains a max selections param if we want the user to only select a limited amount


# Usage Distribution - Tabs
st.write("#")  # simple spacer
st.header("Usage Distribution")
st.write("See which journals were used the most and least for each of the\
          time periods covered by your TR_J1 reports")
#st.caption("Click on each tab to view the specific Fiscal Year")
hist_tab = st.tabs(date_col)

for i, trj1 in enumerate(trj1_list):
    # create a dataframe from the dictionary created earlier so it could be later be dsiplayed or performed with other python functions
    # determine the maximum numbers to better scale the x-axis(max_report) and y-axis(max_count)
    with hist_tab[i]:
        usage_df = occurrences_list[i]
        usage_df = usage_df.rename_axis("Row Index")
        max_count = usage_df[count_header].max()
        max_report = int(usage_df[metric_choice].max())
        chartHeight = 0
        stacked_df = trj1.dataframe

        # create a filter silder and use user input to create a filtered dataframe
        filter_slider = st.slider("Set the minimum and maximum reporting period total (x-axis) here.", 
                                    1, max_report, 
                                    value=(1,max_report)) # slider for user to check a varying range of reporting period totals
        filter_min = filter_slider[0]
        filter_max = filter_slider[1]
        st.write(filter_slider) 
        filter = stacked_df["Reporting_Period_Total"].between(filter_min, filter_max, "both") # returns whether element in Series is between 
        filtered_df = stacked_df[filter]  # creates a filtered dataframe by only including elements that are true from filter variable
        filter_count = len(filtered_df)
        st.write(filter_count)

        # wording based on range and journal count
        if filter_max - filter_min >= 1 and filter_count > 1:
            st.write("There are currently {} journals within the following range: {} - {} reporting period total.".format(filter_count, filter_min, filter_max))
        elif filter_max - filter_min == 0 and filter_count > 1:
            st.write("There are currently {} journals with {} reporting period total.".format(filter_count, filter_min))
        elif filter_max - filter_min >= 1 and filter_count == 1:
            st.write("There is currently {} journal within the following range: {} - {} reporting period total.".format(filter_count, filter_min, filter_max))
        else:
            st.write("There is currently {} journal with {} reporting period total.".format(filter_count, filter_min, filter_max))

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
            # st.dataframe(usage_df, use_container_width=True)
            # st.markdown(usage_df.style.hide(axis="index").to_html(), unsafe_allow_html=True)

        # Responsible for the histogram based on Altair Vega Lite and St.altair_chart
        def get_colors(n): return ["#%06x" %
                                   random.randint(0, 0xFFFFFF) for _ in range(n)]
        color_blind_friendly = [
            "#0077bb", "#33bbee", "#009988", "#ee7733", "#cc3311", "#ee3377", "#bbbbbb"]
        get_colors(50)

        stacked_hist = alt.Chart(filtered_df).mark_bar(width=3).encode(
            alt.X("Reporting_Period_Total:Q", scale=alt.Scale(
                domain=[0, max_report]), title="Reporting Period Total"),
            alt.Y("count()", axis=alt.Axis(grid=False),
                  title="Number of Journals"),
            alt.Detail("Title"),
            #Creates the stacked histogram with which the colors are coded to be be color blind friendly 
            #alt.Color("Title", legend=None, scale=alt.Scale(
                #domain=[title for title in df["Title"]], range=color_blind_friendly)),

            tooltip=["Title", "Reporting_Period_Total"],
        ).interactive().configure_view(height=chartHeight)
        st.write("#")  # simple spacer
        st.altair_chart(stacked_hist, use_container_width=True)

# for i, df_t in enumerate(list_df):
#     with hist_tab[i]:

#         # create a dataframe from the dictionary created earlier so it could be later be dsiplayed or performed with other python functions
#         # determine the maximum numbers to better scale the x-axis(max_report) and y-axis(max_count)
#         usage_df = occurrences_list[i]
#         usage_df = usage_df.rename_axis("Row Index")
#         max_count = usage_df[count_header].max()
#         max_report = int(usage_df[metric_choice].max())
#         chartHeight = 0
#         stacked_df = list_df[i]


#         # create a filter silder and use user input to create a filtered dataframe
#         filter_slider = st.slider("Set the minimum and maximum reporting period total (x-axis) here.", 1, max_report, value=(1,max_report)) # slider for user to check a varying range of reporting period totals
#         filter_min = filter_slider[0]
#         filter_max = filter_slider[1]
#         st.write(filter_slider) 
#         filter = stacked_df["Reporting_Period_Total"].between(filter_min, filter_max, "both") # returns whether element in Series is between 
#         filtered_df = stacked_df[filter]  # creates a filtered dataframe by only including elements that are true from filter variable
#         filter_count = len(filtered_df)

#         st.write(filter_count)

#         # wording based on range and journal count
#         if filter_max - filter_min >= 1 and filter_count > 1:
#             st.write("There are currently {} journals within the following range: {} - {} reporting period total.".format(filter_count, filter_min, filter_max))
#         elif filter_max - filter_min == 0 and filter_count > 1:
#             st.write("There are currently {} journals with {} reporting period total.".format(filter_count, filter_min))
#         elif filter_max - filter_min >= 1 and filter_count == 1:
#             st.write("There is currently {} journal within the following range: {} - {} reporting period total.".format(filter_count, filter_min, filter_max))
#         else:
#             st.write("There is currently {} journal with {} reporting period total.".format(filter_count, filter_min, filter_max))


#         # condition to determine the height for the histogram
#         if max_count >= 300:
#             if max_count >= 300 & max_count <= 600:
#                 chartHeight = 600
#             else:
#                 chartHeight = max_count
#         else:
#             chartHeight = 500

#         # creates a collapsible view of the dataframe containing in details the reporting total, the titles, and the counts of journals
#         with st.expander("Expand to see the filtered data behind the distribution:", expanded=False):
#             st.write("#")  # spacing between text
#             st.caption(
#                 "Click on column header to sort by ascending/descending order")
#             st.dataframe(filtered_df, use_container_width=True)
#             # st.dataframe(usage_df, use_container_width=True)
#             # st.markdown(usage_df.style.hide(axis="index").to_html(), unsafe_allow_html=True)

#         # Responsible for the histogram based on Altair Vega Lite and St.altair_chart
#         def get_colors(n): return ["#%06x" %
#                                    random.randint(0, 0xFFFFFF) for _ in range(n)]
#         color_blind_friendly = [
#             "#0077bb", "#33bbee", "#009988", "#ee7733", "#cc3311", "#ee3377", "#bbbbbb"]
#         get_colors(50)

#         stacked_hist = alt.Chart(filtered_df).mark_bar(width=3).encode(
#             alt.X("Reporting_Period_Total:Q", scale=alt.Scale(
#                 domain=[0, max_report]), title="Reporting Period Total"),
#             alt.Y("count()", axis=alt.Axis(grid=False),
#                   title="Number of Journals"),
#             alt.Detail("Title"),
#             #Creates the stacked histogram with which the colors are coded to be be color blind friendly 
#             #alt.Color("Title", legend=None, scale=alt.Scale(
#                 #domain=[title for title in df["Title"]], range=color_blind_friendly)),

#             tooltip=["Title", "Reporting_Period_Total"],
#         ).interactive().configure_view(height=chartHeight)
#         st.write("#")  # simple spacer
#         st.altair_chart(stacked_hist, use_container_width=True)


#####
# for df in list_df:
#     occurrences = collections.Counter(df["Reporting_Period_Total"])
#     titles = defaultdict(list)
#     # There must be at least one journal linked to rpt, thus we can use a defaultdict and assure that there are no empty lists
#     for index, row in df.iterrows():
#         titles[row["Reporting_Period_Total"]].append(row['Title'])
#         titles_set.add(row['Title'])

#     # create a dictionary that would contain the count numbers, the reporting total, and the titles of the journals
#     count_header = "Number of journals with this many item requests"
#     title_header = "Journals with this many item requests(double-click to see full list)"
#     data = {
#         metric_choice: [key for key, _ in occurrences.items()],
#         count_header: [val for _, val in occurrences.items()],
#         title_header: [val for _, val in titles.items()]
#     }
#     usage_df = pd.DataFrame(data)
#     # max_df_values.append(usage_df[metric_choice].max())
#     occurrences_list.append(usage_df)

# st.sidebar.write("#") # simple spacer

# # multiselect option for titles
# titles_selected = st.sidebar.multiselect(
#     "Click on the titles you want to view on the chart",
#     titles_set
# ) # contains a max selections param if we want the user to only select a limited amount

#####

# # Usage Distribution - Tabs
# st.write("#")  # simple spacer
# st.header("Usage Distribution")
# st.write("See which journals were used the most and least for each of the time periods covered by your TR_J1 reports")
# #st.caption("Click on each tab to view the specific Fiscal Year")
# hist_tab = st.tabs(date_col)
# for i, df_t in enumerate(list_df):
#     with hist_tab[i]:

#         # create a dataframe from the dictionary created earlier so it could be later be dsiplayed or performed with other python functions
#         # determine the maximum numbers to better scale the x-axis(max_report) and y-axis(max_count)
#         usage_df = occurrences_list[i]
#         usage_df = usage_df.rename_axis("Row Index")
#         max_count = usage_df[count_header].max()
#         max_report = int(usage_df[metric_choice].max())
#         chartHeight = 0
#         stacked_df = list_df[i]


#         # create a filter silder and use user input to create a filtered dataframe
#         filter_slider = st.slider("Set the minimum and maximum reporting period total (x-axis) here.", 1, max_report, value=(1,max_report)) # slider for user to check a varying range of reporting period totals
#         filter_min = filter_slider[0]
#         filter_max = filter_slider[1]
#         st.write(filter_slider) 
#         filter = stacked_df["Reporting_Period_Total"].between(filter_min, filter_max, "both") # returns whether element in Series is between 
#         filtered_df = stacked_df[filter]  # creates a filtered dataframe by only including elements that are true from filter variable
#         filter_count = len(filtered_df)

#         st.write(filter_count)

#         # wording based on range and journal count
#         if filter_max - filter_min >= 1 and filter_count > 1:
#             st.write("There are currently {} journals within the following range: {} - {} reporting period total.".format(filter_count, filter_min, filter_max))
#         elif filter_max - filter_min == 0 and filter_count > 1:
#             st.write("There are currently {} journals with {} reporting period total.".format(filter_count, filter_min))
#         elif filter_max - filter_min >= 1 and filter_count == 1:
#             st.write("There is currently {} journal within the following range: {} - {} reporting period total.".format(filter_count, filter_min, filter_max))
#         else:
#             st.write("There is currently {} journal with {} reporting period total.".format(filter_count, filter_min, filter_max))


#         # condition to determine the height for the histogram
#         if max_count >= 300:
#             if max_count >= 300 & max_count <= 600:
#                 chartHeight = 600
#             else:
#                 chartHeight = max_count
#         else:
#             chartHeight = 500

#         # creates a collapsible view of the dataframe containing in details the reporting total, the titles, and the counts of journals
#         with st.expander("Expand to see the filtered data behind the distribution:", expanded=False):
#             st.write("#")  # spacing between text
#             st.caption(
#                 "Click on column header to sort by ascending/descending order")
#             st.dataframe(filtered_df, use_container_width=True)
#             # st.dataframe(usage_df, use_container_width=True)
#             # st.markdown(usage_df.style.hide(axis="index").to_html(), unsafe_allow_html=True)

#         # Responsible for the histogram based on Altair Vega Lite and St.altair_chart
#         def get_colors(n): return ["#%06x" %
#                                    random.randint(0, 0xFFFFFF) for _ in range(n)]
#         color_blind_friendly = [
#             "#0077bb", "#33bbee", "#009988", "#ee7733", "#cc3311", "#ee3377", "#bbbbbb"]
#         get_colors(50)

#         stacked_hist = alt.Chart(filtered_df).mark_bar(width=3).encode(
#             alt.X("Reporting_Period_Total:Q", scale=alt.Scale(
#                 domain=[0, max_report]), title="Reporting Period Total"),
#             alt.Y("count()", axis=alt.Axis(grid=False),
#                   title="Number of Journals"),
#             alt.Detail("Title"),
#             #Creates the stacked histogram with which the colors are coded to be be color blind friendly 
#             #alt.Color("Title", legend=None, scale=alt.Scale(
#                 #domain=[title for title in df["Title"]], range=color_blind_friendly)),

#             tooltip=["Title", "Reporting_Period_Total"],
#         ).interactive().configure_view(height=chartHeight)
#         st.write("#")  # simple spacer
#         st.altair_chart(stacked_hist, use_container_width=True)
st.write("Click on plot and scroll to zoom, click & drag to move, \
         and double-click to reset view. Click ... at top right to \
         download the chart as an SVG/PNG.")