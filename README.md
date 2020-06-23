# Covid19 Indian DashBoard

Application's link: [https://covid19-india-dashboard.herokuapp.com/](https://covid19-india-dashboard.herokuapp.com/)

This is a covid19 Indian Dashboard which was written in streamlit.

Currently it's features are:
* Trend of Total cases in India(Confirmed, Active, Recovered, Deceased)
* A Histogram of active cases across india on a particular date
* Top 10 states based on confirmed cases on a particular date

## Problems which I have faced

* If your streamlit library's version is 0.57+, then your bokeh library's version must be 2.0.0 else, you cannot see any bokeh plot in the dashboard.