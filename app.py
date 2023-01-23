import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import streamlit.components.v1 as components
import json
import collections
from collections import defaultdict
from PIL import Image

# HOW TO RUN APP?
#streamlit run app.py

###############START OF PAGE##################
# Need of title and icon
st.set_page_config(layout="wide", page_icon=None, page_title=None)

# primary_clr = st.get_option("theme.primaryColor")
# txt_clr = st.get_option("theme.textColor")
# # I want 3 colours to graph, so this is a red that matches the theme:
# second_clr = "#d87c7c"
image = Image.open('wesleyan.jpeg')
st.image(image)
# st.title('WELCOME')
st.header("This website is the new way to visualize data from your TR_J1 Reports!")



# upload file - of type csv, json, tsv, or xlsx (read excel can also accept xls, xlsx, xlsm, xlsb, odf, ods and odt)
file_upload = st.file_uploader("", type=['csv', 'tsv', 'xlsx', 'json'])

df = pd.DataFrame()

# upload file -- decision tree for file types
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
cost = st.number_input('Please Input Cost:', min_value=0.00)
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
    "Reporting_Period_Total": [key for key, _ in occurrences.items()],
    "Occurrences": [val for _, val in occurrences.items()],
    "Titles": [val for _, val in titles.items()]
}


usage_df = pd.DataFrame(data)

# st.write(data)
# st.write("Displaying reporting period total, linked with number of books and it's title.")
with st.expander("Expand to see the full list of titles associated with each request:", expanded=False):
    st.dataframe(usage_df, use_container_width=True)

st.subheader("Usage Distribution")
stacked_df = df
stacked_hist = alt.Chart(stacked_df).mark_bar(width=10).encode(
    alt.X("Reporting_Period_Total:Q",title="Reporting Period Total"),
    alt.Y("count()",axis=alt.Axis(grid=False),title="Occurrences"),
    alt.Detail("Title"),
    alt.Color("Title", legend = None),
    # alt.BarConfig(color = "#FF0000"),
    tooltip=["Title","Reporting_Period_Total"],
    # color = "Title"
).interactive().properties(
    height = 400,
    title={
        "text": ["Usage Distribution per book"],
        "subtitle": ["Hover over the bar for more details on specific book titles"],
        "color": "black",
        "subtitleColor": "gray"
    }
)

st.altair_chart(stacked_hist, use_container_width=True)

# config = alt.Legend(titleColor='black', labelFontSize=14) 
# config

###########OTHER###################
#reset row indices after removing first 13 rows
# df.reset_index(drop=True, inplace=True)
# df.replace(np.nan, 0, regex=True, inplace = True)

# REMOVE LAST ROW (TOTAL UNIQUE REQUESTS) AND SAVE IT INTO VAR
# total_unique_requests = df.iloc[[len(df)-1]]
# print(total_unique_requests.to_string())
# df = df.iloc[:len(df)-1]

# #Use css file to style
# with open ('style.css') as f:
#     st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# st.subheader('Look into the authorships, citations, and downloads of each journal')
# auth_hist = alt.Chart(df).mark_bar(width=10).encode(
#     alt.X('authorships:Q', title="Authorships (average per year over the next five years)"),
#     alt.Y('count()', axis=alt.Axis(grid=False)),
#     alt.Detail('index'),
#     tooltip=['title', 'authorships', 'subscription_cost', 'subscribed'],
#     color=alt.Color('subscribed:N', scale=subscribed_colorscale)
#     ).interactive().properties(
#         height=400,
#         title={
#             "text": ["Authorships Distribution"],
#             "subtitle": ["What do the range of Authorships look like?", "Use this graph to help set the Authorships slider filter and narrow down titles of interest"],
#             "color": "black",
#             "subtitleColor": "gray"
#         }
#         )
# st.altair_chart(auth_hist, use_container_width=True)








# subscribed_colorscale = alt.Scale(domain = ['TRUE', 'FALSE', 'MAYBE', ' '],
#                                   range = ['blue', 'red', 'green', 'gray'])

# x = st.slider('Select a value', key=0)
# st.write(x, 'squared is', x * x)

# y = st.slider('Select a value', key=1)
# st.write(y, 'squared is', y * y * y)

# color = st.select_slider(
#     'Select a color of the rainbow',
#     options=['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet'])
# st.write('My favorite color is', color)


# components.html(
#     """
# <html>
# <body>
# <script>var clicky_site_ids = clicky_site_ids || []; clicky_site_ids.push(101315881);</script>
# <script async src="//static.getclicky.com/js"></script>
# <noscript><p><img alt="Clicky" width="1" height="1" src="//in.getclicky.com/101315881ns.gif" /></p></noscript>
# </body>
# </html>
#     """
# )


# st.subheader('Look into the authorships, citations, and downloads of each journal')
# auth_hist = alt.Chart(df).mark_bar(width=10).encode(
#     alt.X('authorships:Q', title="Authorships (average per year over the next five years)"),
#     alt.Y('count()', axis=alt.Axis(grid=False)),
#     alt.Detail('index'),
#     tooltip=['title', 'authorships', 'subscription_cost', 'subscribed'],
#     color=alt.Color('subscribed:N', scale=subscribed_colorscale)
#     ).interactive().properties(
#         height=400,
#         title={
#             "text": ["Authorships Distribution"],
#             "subtitle": ["What do the range of Authorships look like?", "Use this graph to help set the Authorships slider filter and narrow down titles of interest"],
#             "color": "black",
#             "subtitleColor": "gray"
#         }
#         )
# st.altair_chart(auth_hist, use_container_width=True)
# https://realpython.com/python-csv/


# P1 (First priority):
# Read in 1 COUNTER TR_J1 sheet
# Read in 1 user-inputed cost for all journals in the sheet
# Calculate cost per use 
# Plot histogram of use distribution with possibility to hover to see different journals 
# Interactivity with histogram
# Save plots to png or svg (or other desired formats)

# How do we calculate cost per use?
# Plot histogram of use distribution with possibility to hover to see different journals 


'''
Next Steps:

colorblind friendly?
JSON!
fix chart gaps
'''