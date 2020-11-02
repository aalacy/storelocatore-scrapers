import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from datetime import datetime


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
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    return_main_object = []
    zips = sgzip.for_radius(100)
    addresses = []
    r = session.get("https://intl.target.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for script in soup.find_all("script"):
        if '"apiKey":' in script.text:
            api_key = script.text.split('"apiKey":')[1].split(",")[0].replace('"',"")
    for zip_code in zips:
        try:
        
            base_url = "https://intl.target.com"
            r = session.get("https://redsky.target.com/v3/stores/nearby/" + str(zip_code) + "?key=" + str(api_key) + "&limit=1000&within=100&unit=mile",headers=headers)
            data = r.json()[0]["locations"]
            for store_data in data:
                store = []
                store.append("https://intl.target.com")
                store.append(store_data["location_names"][0]["name"])
                store.append(store_data["address"]["address_line1"] + store_data["address"]["address_line2"] if "address_line2" in store_data["address"] else store_data["address"]["address_line1"])
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(store_data["address"]["city"])
                store.append(store_data["address"]["region"])
                store.append(store_data["address"]["postal_code"])
                store.append("US")
                store.append(store_data["location_id"])
                store.append(store_data["contact_information"]["telephone_number"])
                store.append("target")
                store.append(store_data["geographic_specifications"]["latitude"])
                store.append(store_data["geographic_specifications"]["longitude"])
            
                location_request = session.get("https://redsky.target.com/v3/stores/location/" + str(store_data["location_id"]) + "?key=" + str(api_key), headers=headers)
                hours = ""
                store_hours = location_request.json()[0]["rolling_operating_hours"]["regular_event_hours"]["days"]
                for i in range(0,7):
                    if store_hours[i]["is_open"] == True:
                        hours = hours + " " + store_hours[i]["day_name"] + " " + datetime.strptime(store_hours[i]["hours"][0]["begin_time"], "%H:%M:%S").strftime("%I:%M %p") + " - " + datetime.strptime(store_hours[i]["hours"][0]["end_time"], "%H:%M:%S").strftime("%I:%M %p")
                    else:
                        hours = hours + " " + store_hours[i]["day_name"] + " Closed"
                store.append(hours if hours != "" else "<MISSING>")
                
                return_main_object.append(store)
        except:
            continue        
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
