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

