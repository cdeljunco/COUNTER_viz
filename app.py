import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import streamlit.components.v1 as components
import json
import collections
import random
from collections import defaultdict
from PIL import Image
from datetime import datetime


# Set the layout of the Streamlit
st.set_page_config(layout="wide", page_icon=None, page_title="Counter Visualization")

# primary_clr = st.get_option("theme.primaryColor")
# txt_clr = st.get_option("theme.textColor")
# # I want 3 colours to graph, so this is a red that matches the theme:
# second_clr = "#d87c7c"

#Main image and header 
image = Image.open('header.jfif')
st.image(image)
st.header("This website is the new way to visualize data from your TR_J1 Reports!")

# Upload file - of type csv, json, tsv, or xlsx (read excel can also accept xls, xlsx, xlsm, xlsb, odf, ods and odt)
file_upload = st.file_uploader("Please upload one unedited spreadsheet per year of data.", type=['csv', 'tsv', 'xlsx', 'json'], accept_multiple_files=True)

# Create a variable to represent an empty Panda Dataframe, create an empty list to hold list of DataFrames
df = pd.DataFrame()
list_df = []
file_names = []
file_count = 0

# Decision Tree to upload the files
# for file in file_upload:
if file_upload:
    file_count = len(file_upload)
    for file in file_upload:
        if file.type == "text/csv":
            df = pd.read_csv(file, skiprows=13, index_col=False)
        elif file.type == "application/json":
            json_temp = json.load(file)
            file = json_temp["Report_Items"]
            st.json(json_temp)
            df = file
            #df = pd.read_json(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": #xslx file
            df = pd.read_excel(file, skiprows=13)
        elif file.type == "text/tab-separated-values":
            df = pd.read_csv(file, sep='\t', skiprows=13)
        else:
            st.warning('Warning: Please upload a file of the correct type as listed above.', icon="⚠️")
        list_df.append(df)
        file_names.append(file.name)

    
    # wording based on files uploaded
    if len(file_upload) > 1:
        st.success(str(file_count) + " files uploaded successfully!", icon="✅")
    elif len(file_upload) ==  1:
        st.success("File uploaded successfully!", icon="✅")
else:
    df = pd.read_csv("Royal Society of Chemistry-TR_J1-2020 July-2022 June.csv", skiprows=13, index_col=False) # use default data
    list_df.append(df)
    file_names.append("Royal Society of Chemistry-TR_J1-2020 July-2022 June.csv")
    file_count = len(list_df)


# cleaning data by dropping unecessary rows and coverting NaN types to 0
df = df.drop(columns=["Publisher","Publisher_ID","Platform","DOI","Proprietary_ID","Print_ISSN","Online_ISSN","URI"])
df.replace(np.nan, 1, regex=True, inplace = True)


# Accurately gets all dates for each file and saves it to a dict 
# key = name of file, val = list of dates
df_dates = {}
i = 0
for given_df in list_df:
    # st.write(given_df)
    col_names = list(given_df.columns)[11:]
    if len(col_names) < 12:
        st.warning('Warning: Our records indicate that you have less than 12 months of data for one of your uploaded files.', icon="⚠️")
    df_dates[file_names[i]] = col_names
    i+=1

# checks if files have data for the same month, can be updated to say which files possibly
distinct_dates = []
for file, date_range in df_dates.items():
    for date in date_range:
        if date in distinct_dates:
            st.error('Our records indicate that your two of your uploaded files have data for the same month. Please fix this error before moving forward.', icon="🚨")
        else:
            distinct_dates.append(date)

st.write("#") # simple spacer

# wording based on number of files uploaded
if len(list_df) > 1:
    st.subheader("You have successfully uploaded " + str(len(list_df)) + " files with the following details:")
elif len(list_df) ==  1:
    st.subheader("You have successfully uploaded a file with the following details:")

# Identify Unique Journals per TRJ1 file
unique_journals = []
for given_df in list_df:
    unique_journals.append(len(given_df.loc[given_df['Metric_Type'] == 'Unique_Item_Requests']))

#listing dates based off either it is date time class or string
date_col = []
for date_range in df_dates.values():
    if type(date_range[0]) != datetime:
        date_col.append(date_range[0] + " - " + date_range[-1])
    else:
        date_col.append(date_range[0].strftime("%m/%Y") + " - " + date_range[-1].strftime("%m/%Y"))

# saving file data into one hashmap
file_data = {
    "File Name": [file for file in df_dates],
    "Date Range": [date for date in date_col], 
    "Number of Journals": [num for num in unique_journals]
}

#creates a collapsible view of the dataframe containing in details the reporting total, the titles, and the counts of journals
with st.expander("Expand to see the full details of each uploaded file:", expanded=False):
    #convert files' data into dataframe and display it, setting to max width
    file_df = pd.DataFrame(file_data)
    st.dataframe(file_df, use_container_width=True)


############### Streamlit radio for Metric Type ##############
st.write("#") # simple spacer
st.markdown("Learn more about <a href='https://www.projectcounter.org/about/'>COUNTER</a>.", unsafe_allow_html=True)
# https://medialibrary.projectcounter.org/file/The-Friendly-Guide-for-Librarians
#Decision Tree for whether there exists more than one metric type on file
if 'Unique_Item_Requests' in df['Metric_Type'].values and "Total_Item_Requests" in df['Metric_Type'].values:
    metric_choice = st.radio(
    "Please select a Metric Type",
    ("Unique Item Requests","Total Item Requests")
    )
elif 'Unique_Item_Requests' in df['Metric_Type'].values and "Total_Item_Requests" not in df['Metric_Type'].values:
    metric_choice = st.radio(
    "Please select a Metric Type",
    ("Unique Item Requests","Total Item Requests"), disabled=True
    )
elif 'Unique_Item_Requests' not in df['Metric_Type'].values and "Total_Item_Requests" in df['Metric_Type'].values:
    metric_choice = st.radio(
    "Please select a Metric Type",
    ("Total Item Requests","Unique Item Requests"), disabled=True
    )
else:
    st.warning(st.warning('Please make sure that you have a valid metric type of Total Item Requests or Unique Item Requests', icon="⚠️"))


if metric_choice == "Unique Item Requests":
    df = df.loc[df['Metric_Type'] == "Unique_Item_Requests"]
    df = df.drop(columns="Metric_Type")
else:
    df = df.loc[df['Metric_Type'] == "Total_Item_Requests"]
    df = df.drop(columns="Metric_Type")
################ Determine the report total based on whether "Total Unqiue Item Requests" exist in the "Title" column

# if df contains row for reporting period total, take that, else sum column
if df.iat[len(df)-1, 0] == "Total unique item requests:":   # check if sum exists in file
    rpt = df.iat[len(df) - 1, 1]
    df = df.iloc[:len(df)-1]
else:
    rpt = df['Reporting_Period_Total'].sum()

############### Streamlit: Displaying Data #################

# cost input, shows warning alert if no input, else success alert and display cost per report
cost = st.number_input('Please input journal package cost in dollar amount:', min_value = 0.00, format="%f")
if not cost or cost < 0:
    st.warning("Please input a valid cost!", icon="⚠️")
else:
    st.subheader("Based on your input, your total cost per use is calculated below")
    cpt = format(cost/rpt, ".2f")
    st.write("$ " + cpt)


# using counter to get occurences of each num
occurrences = collections.Counter(df["Reporting_Period_Total"])
titles = defaultdict(list)

#There must be at least one journal linked to rpt, thus we can use a defaultdict and assure that there are no empty lists
for index, row in df.iterrows():
    titles[row["Reporting_Period_Total"]].append(row['Title'])

# create a dictionary that would contain the count numbers, the reporting total, and the titles of the journals
data = {
    "Reporting Period Total": [key for key, _ in occurrences.items()],
    "Number of Journals": [val for _, val in occurrences.items()],
    "Titles (Double click to see full list)": [val for _, val in titles.items()]
}

# create a dataframe from the dicitionary created earlier so it could be later be dsiplayed or performed with other python functions 
usage_df = pd.DataFrame(data)

# determine the maximum numbers to better scale the x-axis(max_report) and y-axis(max_count)
max_count = usage_df["Number of Journals"].max()
max_report = usage_df["Reporting Period Total"].max()
chartHeight = 0
#condition to determine the height for the histogram 
if max_count >= 300:
    if max_count >= 300 & max_count <= 600:
        chartHeight = 600
    else:
        chartHeight = max_count
else:
    chartHeight = 500


st.subheader("Usage Distribution")
#creates a collapsible view of the dataframe containing in details the reporting total, the titles, and the counts of journals
with st.expander("Expand to see the full list of titles associated with each request:", expanded=False):
    st.write("#") # spacing between text
    st.caption("Click on column title to order by ascending/descending order")
    st.dataframe(usage_df, use_container_width=True)
    # st.markdown(usage_df.style.hide(axis="index").to_html(), unsafe_allow_html=True)


#Responsible for the histogram based on Altair Vega Lite and St.altair_chart
get_colors = lambda n: ["#%06x" % random.randint(0, 0xFFFFFF) for _ in range(n)]
color_blind_friendly = ["#0077bb","#33bbee","#009988","#ee7733","#cc3311","#ee3377","#bbbbbb"]
get_colors(50)
stacked_df = df
stacked_hist = alt.Chart(stacked_df).mark_bar(width=3).encode(
    alt.X("Reporting_Period_Total:Q",scale = alt.Scale(domain=[0,max_report]),title="Reporting Period Total"),
    alt.Y("count()",axis=alt.Axis(grid=False),title="Number of Journals"),
    alt.Detail("Title"),
    alt.Color("Title", legend = None, scale=alt.Scale(domain=[title for title in df["Title"]], range=color_blind_friendly)),
    tooltip=["Title","Reporting_Period_Total"],
).interactive().configure_view(height = chartHeight)
st.write("#") # simple spacer
st.altair_chart(stacked_hist, use_container_width=True)
st.markdown("<p style='text-align: center;'>Click on the three dots on the top right to download the chart as an SVG/PNG.</p>", unsafe_allow_html=True)