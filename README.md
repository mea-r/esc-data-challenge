# MACROECONOMIC IMPACT OF THE 2022 INVASION

Dashboard created to support submission for ESC Data Challenge.

## Running the dashboard

To run the dashboard:

```bash
streamlit run v1/dashboard.py
```

The folder v1 contains all program files responsible for the visuals. The data folder holds all the data used for figures that do not rely on APIs. It also contains some duplication of our program files, which we used for testing purposes. The .gitignore and requirements.txt are in-house files used by our team to manage workflow.

s1 represents the first section of the report - Price stability. The folder contains code specific to each figure.

The files s2.visualization.py and s3_visualization differ in a way: figures are not explicitly split into different program files, but instead, all figures are generated in one script. In other words, s2_visualization houses all program code for section 2 of the report - Economic growth. Similarly, s3_visualization contains all code relevant to all figures in section 3 of the report - Current account.

The data_fetcher.py file uses the requests library to pull data from the ECB's site. This represents some of the data used in the figures.

The dashboard.py file is responsible for the overall look of the website https://esc-data-challenge.streamlit.app/

The overview_charts.py is responsible for the figures on the website https://esc-data-challenge.streamlit.app/

Finally, the theme.py file is used to create a homogenous look across all our infographics.
