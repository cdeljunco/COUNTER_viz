![92 Theater, Wesleyan](readme.jpg)

# COUNTER_viz

## About

COUNTER_viz is a data visualization tool that enables libraries to upload TRJ1 files to get a sense of which journals are being utilized to make appropriate cost-benefit decisions. The application uses [Altair](https://altair-viz.github.io/index.html) to develop interactive graphs where the user can zoom and hover for the best user experience. The website was developed using [Streamlit](https://streamlit.io/), an open source app framework in Python language. 

<br />

**Before getting started, make sure you have downloaded all of the proper packages and dependencies.**

## Prerequisites

1. Install [Python 3.7-3.10](https://www.python.org/downloads/) (Streamlit does not currently support Python 3.11)
2. Install [PIP management system](https://pip.pypa.io/en/stable/installation/) (v22.3.1)

### File requirements

1. Your TRJ1 file must be of type csv, tsv, or xlsx.

2. It must remain unchanged after downloading it from your directory.
3. Ensure the following columns exist in your files:
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

## Projected Cost Per Use Feature

A predicted cost per usage will be determined based on the inputted cost for that year if one of the supplied TRJ1 files has less than 12 months of data. The projected cost per use is estimated using the cost per use from the prior fiscal years, provided that they all have 12 months of data.

# Run Streamlit App

1. Clone the streamlit app to a directory of choice

```python
git clone git@github.com:cdeljunco/COUNTER_viz.git
```

2. Change working directory of your terminal to the COUNTER_viz folder

```python
streamlit run app.py
```

:warning: **Make sure that you are running on Streamlit version 1.15.1 or later.**
