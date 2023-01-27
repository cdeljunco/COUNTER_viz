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
        # file_upload = file_upload["Report_Items"]
        # file_upload = json.load(file_upload)
        # json_file = json.load(file_upload)
        # print(file_upload)
        json_temp = json.load(file_upload)
        file_upload = json_temp["Report_Items"]
        st.json(json_temp)
        df = file_upload
        # file_upload.remove("Report_Header")
        # df = pd.read_json(file_upload)
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
df = df.drop(columns=["Publisher","Publisher_ID","Platform","DOI","Proprietary_ID","Print_ISSN","Online_ISSN","URI","Metric_Type"])
df.replace(np.nan, 0, regex=True, inplace = True)



# if df contains row for reporting period total, take that, else sum column
if df.iat[len(df)-1, 0] == "Total unique item requests:":   # check if sum exists in file
    rpt = df.iat[len(df) - 1, 1]
    df = df.iloc[:len(df)-1]
else:
    rpt = df['Reporting_Period_Total'].sum()


############### Streamlit: Displaying Data #################

# cost input, shows warning alert if no input, else success alert and display cost per report
cost = st.number_input('Please Input journal package cost:', min_value=0.00)
if not cost or cost < 0:
    st.warning("Please input a valid cost!", icon="⚠️")
else:
    st.subheader("Based on your input, your total cost per use is calculated below")
    cpt = format(cost/rpt, ".2f")
    st.write(cpt)


# using counter to get occurences of each num
occurrences = collections.Counter(df["Reporting_Period_Total"])

titles = defaultdict(list)

#There must be at least one book linked to rpt, thus we can use a defaultdict and assure that there are no empty lists
for index, row in df.iterrows():
    titles[row["Reporting_Period_Total"]].append(row['Title'])


# data that was produced to create histogram
data = {
    "Reporting Period Total": [key for key, _ in occurrences.items()],
    "Number of Journals": [val for _, val in occurrences.items()],
    "Titles (Double click to see full list)": [val for _, val in titles.items()]
}
usage_df = pd.DataFrame(data)
max_count = usage_df["Number of Journals"].max()
max_report = usage_df["Reporting Period Total"].max()
st.text(max_count)
st.text(max_report)

st.subheader("Usage Distribution")
with st.expander("Expand to see the full list of titles associated with each request:", expanded=False):
    st.dataframe(usage_df, use_container_width=True)

stacked_df = df
stacked_hist = alt.Chart(stacked_df).mark_bar(width=10).encode(
    alt.X("Reporting_Period_Total:Q",title="Reporting Period Total"),
    alt.Y("count()",axis=alt.Axis(grid=False),title="Occurrences"),
    alt.Detail("Title"),
    alt.Color("Title", legend = None),
    tooltip=["Title","Reporting_Period_Total"],
).interactive()
st.altair_chart(stacked_hist, use_container_width=True)