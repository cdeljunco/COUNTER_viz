# COUNTER_viz app

## About

COUNTER_viz is a data visualization tool that enables libraries to upload TR_J1 COUNTER reports and visualize the usage distribution of journals inha given year; compare usage of individual journals year-over-year; calculate the cost per use of journal packages; and estimate the cost-per-use for incomplete years of data. 

The application is written in Python and uses [Altair](https://altair-viz.github.io/index.html) to develop interactive graphs and [Streamlit](https://streamlit.io/) to deploy as a website.

The app can be used [online](http://userphp.wesleyan.edu:8501/) when connected to the Wesleyan WiFi network or VPN, or run locally using the instructions below.

## Running the app locally

<u>Prerequisites</u>

1. Any version of [Python 3.7-3.10](https://www.python.org/downloads/) (Streamlit does not currently support Python 3.11) *except* 3.9.7
2. Python packages: streamlit \geq v1.15.1, altair, plotly, datetime, pandas, typing, numpy, os

<u>How to run locally</u>

1. Clone the streamlit app to a directory of choice

```python
git clone git@github.com:cdeljunco/COUNTER_viz.git
```

2. Change working directory of your terminal to the COUNTER_viz folder

```python
streamlit run app.py
```

:warning: **Make sure that you are running on Streamlit version 1.15.1 or later.**

## Using the app

### File requirements

1. Your TR_J1 report must be of type csv, tsv, or xlsx

2. Do not modify the TR_J1 report before uploading; it should contain the following columns:
   
   * Title
   * Publisher
   * Publisher_ID
   * Platform
   * DOI
   * Proprietary_ID
   * Print_ISSN
   * Online_ISSN
   * Sn
   * URI
   * Metric_Type
   * Reporting_Period_Total

### Projected Cost Per Use

A predicted cost per usage will be determined based on the inputed cost for that year if one of the uploaded TR_J1 reports has less than 12 months of data. The projected cost per use is estimated based on the TR_J1 data you upload for prior complete fiscal years, provided that they all have 12 months of data. This is useful for estimating the cost per use of the current year.

## Files

- `app.py`: main program

- `trj1.py`: implements the TRJ1 class which stores parameters such as beginning and end dates, cost per use, and total usage for each TR_J1 report uploaded

- `projections.py`: functions for calculating the projected cost per use

- `helper_fxns.py`: miscellaneous functions for reading files, selecting the metric type, sorting TR_J1 objects chronologically, and checking for errors and incomplete data in uploaded files

- `figures.py`: functions for plotting the figures
