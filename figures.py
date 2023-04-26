import pandas as pd
import altair as alt
import plotly.express as px
import streamlit as st

def linePlot(date_col, cpuDF):
    # Cost per use line graph for all of the attached journals
    cpuData = {
        "Date Range": date_col,
        "Cost Per Use": cpuDF
    }
    # Create a dataframe from the given data range and the CPU per fiscal year
    cpuDataFrame = pd.DataFrame(cpuData)
    fig1 = px.line(cpuDataFrame,
                    x="Date Range",
                    y="Cost Per Use")
    return (fig1,cpuDataFrame)

#create a histogram showing the distributions of Journals based on the Reporting Period Total
def histogram(dataframe,filter_max,chartHeight):
    return (
        alt.Chart(dataframe)
        .mark_bar(width=3)
        .encode(
            alt.X(
                "Reporting_Period_Total:Q",
                scale=alt.Scale(domain=[0, filter_max]),
                title="Reporting Period Total",
            ),
            alt.Y(
                "count()",
                axis=alt.Axis(grid=False),
                title="Number of Journals",
            ),
            alt.Detail("Title"),
            tooltip=["Title", "Reporting_Period_Total"],
        )
        .interactive()
        .configure_view(height=chartHeight)
    )


# Create a bar chart with color corresponding to the fiscal years
@st.cache_data
def barChart(dataframe):
    return px.bar(
        dataframe,
        x="Title",
        y="Reporting_Period_Total",
        color="Fiscal_Year",
        barmode="group",
        color_discrete_sequence=[
            '#D81B60',
            '#1E88E5',
            '#FFC107',
            "#004D40",
            "#E48DF6",
            "#FA01B8",
            "#C16B04",
        ],
        labels={
            "Title": "Journal Title",
            "Reporting_Period_Total": "Reporting Period Total",
        },
    )

