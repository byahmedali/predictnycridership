import streamlit as st
from datetime import date
import requests
import urllib.request
import json
import os
import ssl

st.title("NYC Taxi Ridership Prediction")

st.markdown('''

This app uses the services and analysis developed by the ATS Data Analysis team to provide a prediction of the total number of trips on any given day in NYC. 
The data source is the publically available NYC Trips data. The data is cleaned, parsed, and transformed using Azure Databricks to easily extract the necessary features for ML training. Then the Azure ML Studio is used to train the model on data from the duration of 01/01/2021 to 31/12/2022. The endpoint API is deployed on Azure Services and can be accessed through a server link. This web app is deployed using Azure Web Application ready to provide trends and predictions based on the necessary inputs. 
The inputs required for this prediction are:
- The Trip Origin Borough 
- The Date for the Prediction
- The Ride Type 

This prediction model enables taxi and for-hire-vehicle dispatching services with an estimate of the daily number of trips originating at a given borough in NYC on any given day. The City of New York can use this information to better manage its fleet and more accurately meet demand. This helps them reduce wait times, have a lower number of idle vehicles, less wasted resources, and mitigate their negative contribution to traffic and the environment. 

You can try the prediction model below yourself.
''')

st.write("You can adjust some parameters according to your need.")

pickup_location = st.selectbox("Pickup Location in New York City", ["Manhattan", "Bronx", "Brooklyn", "EWR", "Queens", "Staten Island"])

selected_date = st.date_input("Date in the future", date(2023, 1, 1))
year = int(selected_date.year)
month = int(selected_date.month)
day = int(selected_date.day)

selected_day = selected_date.strftime("%A")[0:3]
#st.write(f"You selected {selected_day} in week")
if selected_day in ["Mon","Tue","Wed","Thu","Fri"]:
  workday=1
elif selected_day in ["Sat", "Sun"]:
  workday=0

# season_dict={ [['12','1','2']]:"Winter",[['3','4','5']]:"Spring",[['6','7','8']]:"Summer",[['9','10','11']]:"Autumn"}
# season_dict={ ['12','1','2']:"Winter",['3','4','5']:"Spring",['6','7','8']:"Summer",['9','10','11']:"Autumn"}
# season_dict={ "Winter":['12','1','2'],"Spring":['3','4','5'],"Summer":['6','7','8'],"Autumn":['9','10','11']}

if month in [12, 1, 2]:
    season="Winter"
elif month in [3, 4, 5]:
  season="Spring"
elif month in [6, 7, 8]:
    season="Summer"
elif month in [9, 10, 11]:
    season="Autumn"
# for month_index in season_dict.keys():
    # print(month)
    # if True:
        # print(season_dict.get())
        # print("hkjhkhkjh")
# season = st.selectbox("Select a season", ["Spring", "Summer", "Fall", "Winter"])
taxi_type = st.selectbox("Ride type", ["Green Taxi", "Yellow Taxi", "High Volume For-Hire Vehicle"])

#st.write(pickup_location)
#st.write(taxi_type)
#st.write(selected_date)
#st.write(year)
#st.write(month)
#st.write(day)
#st.write(selected_day)
#st.write(workday)
#st.write(season)
#  -------------------------------------

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context
allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
data =  {
  "Inputs": {
    "data": [
      {
        "PickupBorough": pickup_location, #Bronx, Brooklyn, EWR, Manhattan, Queens, Staten Island.
        "RideType": taxi_type, #Green Taxi, Yellow Taxi, High Volume For-Hire Vehicle.
        "Year": year, # 2021, 2022, 2023..
        "Month": month, # 1 - 12
        "Day": day, # 1 - 31
        "Season": season, #Spring, Summer, Autumn, Winter
        "DayOfWeek": selected_day, #Sun, Mon, Tue, Wed, Thu, Fri, Sat
        "Workday": workday # 1 (Yes), 0 (No)
      }
    ]
  },
  "GlobalParameters": 1.0
}


body = str.encode(json.dumps(data))
#st.write(body)
url = 'http://ff8b8ccf-0dfb-48f0-b6f3-5e7954b6d1c6.eastus.azurecontainer.io/score'


headers = {'Content-Type':'application/json'}
req = urllib.request.Request(url, body, headers)
if st.button("Use AI to Predict"):
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        result = result["Results"][0]
        st.write("Expected Number of Trips:" )
        if result < 0:
          st.title(0)
        elif result >= 0:
          st.title(int(round(result)))
        st.write(f"On  {year}-{month}-{day}.")

        # st.write(f"The ride count is {int(round(result['Results'][0],3))} \t At:>  DATE: {year}-{month}-{day}")
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        st.write("The request failed with status code: " + str(error.code))
        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))

# api_call(data)