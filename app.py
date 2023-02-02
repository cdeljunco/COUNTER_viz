import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import streamlit.components.v1 as components
import json
import collections
from collections import defaultdict
from PIL import Image

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
file_upload = st.file_uploader("", type=['csv', 'tsv', 'xlsx', 'json'])

# Create a variable to represent an empty Panda Dataframe
df = pd.DataFrame()

# Decision Tree to upload the files
if file_upload:
    if file_upload.type == "text/csv":
        df = pd.read_csv(file_upload, skiprows=13)
    elif file_upload.type == "application/json":
        json_temp = json.load(file_upload)
        file_upload = json_temp["Report_Items"]
        st.json(json_temp)
        df = file_upload
        #df = pd.read_json(file_upload)
    elif file_upload.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": #xslx file
        df = pd.read_excel(file_upload, skiprows=13)
    elif file_upload.type == "text/tab-separated-values":
        df = pd.read_csv(file_upload, sep='\t', skiprows=13)
    else:
        st.warning('Please upload a file of the correct type as listed above.', icon="⚠️")
    st.success("File Uploaded!", icon="✅")
else:
    df = pd.read_csv("./IOP-JR1_TR_J1-FY19 to FY22 - TR_J1-FY20.csv", skiprows=13) # use default data



# cleaning data by dropping unecessary rows and coverting NaN types to 0
df = df.drop(columns=["Publisher","Publisher_ID","Platform","DOI","Proprietary_ID","Print_ISSN","Online_ISSN","URI"])
df.replace(np.nan, 0, regex=True, inplace = True)


############### Streamlit radio for Metric Type ##############
metric_choice = st.radio(
    "Please select a Metric Type",
    ("Unique Item Requests","Total Item Requests")
)

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
cost = st.number_input('Please Input journal package cost in dollar:', min_value = 0.00, format="%f")
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
if max_count >= 500:
    if max_count >= 800:
        chartHeight = 800
    else:
        chartHeight = max_count
else:
    chartHeight = 500


st.subheader("Usage Distribution")
#creates a collapsible view of the dataframe containing in details the reporting total, the titles, and the counts of journals
with st.expander("Expand to see the full list of titles associated with each request:", expanded=False):
    st.dataframe(usage_df, use_container_width=True)

#Responsible for the histogram based on Altair Vega Lite and St.altair_chart
stacked_df = df
stacked_hist = alt.Chart(stacked_df).mark_bar(width=10).encode(
    alt.X("Reporting_Period_Total:Q",scale = alt.Scale(domain=[0,max_report]),title="Reporting Period Total"),
    alt.Y("count()",axis=alt.Axis(grid=False),title="Number of Journals"),
    alt.Detail("Title"),
    alt.Color("Title", legend = None),
    tooltip=["Title","Reporting_Period_Total"],
).interactive().configure_view(height = chartHeight)
st.altair_chart(stacked_hist, use_container_width=True)