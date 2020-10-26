import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    base_url = "https://www.monarchdental.com"
    return_main_object = []
    for i in range(len(states)):
        state_request = session.get("https://api.smilebrands.com/public/facility/search/state/" + states[i],headers=headers)
        if state_request.json()["success"] == True:
            data = state_request.json()["data"]
            for k in range(len(data)):
                store_data = data[k]
                store = []
                store.append("https://www.monarchdental.com")
                store.append(store_data["name"])
                store.append(store_data["address"] + store_data["careOf"] if "careOf" in store_data and store_data["careOf"] != None else store_data["address"])
                store.append(store_data["city"])
                store.append(store_data["state"])
                store.append(store_data["zip"])
                store.append("US")
                store.append(store_data["id"])
                store.append(store_data["phoneNumber"])
                store.append("monarch dental")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                print(store_data["id"])
                location_request = session.get("https://api.smilebrands.com/public/facility/id/" + str(store_data["id"]),headers=headers)
                if location_request.json()["success"] == False:
                    continue
                store_hours = location_request.json()["data"]
                hours = ""
                if "sundayHours" in store_hours and store_hours["sundayHours"] != None:
                    hours = hours + " sundayHours " + store_hours["sundayHours"]
                if "mondayHours" in store_hours and store_hours["mondayHours"] != None:
                    hours = hours + " mondayHours " + store_hours["mondayHours"]
                if "tuesdayHours" in store_hours and store_hours["tuesdayHours"] != None:
                    hours = hours + " tuesdayHours " + store_hours["tuesdayHours"]
                if "wednesdayHours" in store_hours and store_hours["wednesdayHours"] != None:
                    hours = hours + " wednesdayHours " + store_hours["wednesdayHours"]
                if "thursdayHours" in store_hours and store_hours["thursdayHours"] != None:
                    hours = hours + " thursdayHours " + store_hours["thursdayHours"]
                if "fridayHours" in store_hours and store_hours["fridayHours"] != None:
                    hours = hours + " fridayHours " + store_hours["fridayHours"]
                if "saturdayHours" in store_hours and store_hours["saturdayHours"] != None:
                    hours = hours + " saturdayHours " + store_hours["saturdayHours"]
                store.append(hours if hours != "" else "<MISSING>")
                print(store)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
