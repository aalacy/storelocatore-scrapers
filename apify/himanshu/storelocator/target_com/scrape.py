import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from datetime import datetime


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    app_key_request = session.get("https://www.target.com/store-locator/find-stores",headers=headers)
    app_key_soup = BeautifulSoup(app_key_request.text,"lxml")
    for script in app_key_soup.find_all("script"):
        if "apiKey" in script.text:
            app_key = json.loads(script.text.split("window.__PRELOADED_STATE__= ")[1])["config"]["firefly"]["apiKey"]
    for zip_code in zips:
        base_url = "https://www.target.com"
        r = session.get("https://redsky.target.com/v3/stores/nearby/"+ str(zip_code) + "?key=" + app_key + "&limit=100000&within=100&unit=mile",headers=headers)
        page_url="https://redsky.target.com/v3/stores/nearby/"+ str(zip_code) + "?key=" + app_key + "&limit=100000&within=100&unit=mile"
        for store_data in r.json()[0]["locations"]:
            store = []
            store.append("https://www.target.com")
            store.append(store_data["location_names"][0]["name"])
            store.append(store_data["address"]["address_line1"] + " " + store_data["address"]["address_line2"] if "address_line2" in store_data["address"] else store_data["address"]["address_line1"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["address"]["city"])
            store.append(store_data["address"]["region"])
            store.append(store_data["address"]["postal_code"])
            store.append("US")
            store.append(store_data["location_id"])
            store.append(store_data["contact_information"]["telephone_number"])
            store.append("<MISSING>")
            store.append(store_data["geographic_specifications"]["latitude"])
            store.append(store_data["geographic_specifications"]["longitude"])
            store.append(page_url)
           
            while True:
                try:
                   
                    location_request = session.get("https://redsky.target.com/v3/stores/location/" + str(store_data["location_id"]) + "?key=" + str(app_key), headers=headers)
                    hours = ""
                    store_hours = location_request.json()[0]["rolling_operating_hours"]["regular_event_hours"]["days"]
                    for i in range(0,7):
                        if store_hours[i]["is_open"] == True:
                            hours = hours + " " + store_hours[i]["day_name"] + " " + datetime.strptime(store_hours[i]["hours"][0]["begin_time"], "%H:%M:%S").strftime("%I:%M %p") + " - " + datetime.strptime(store_hours[i]["hours"][0]["end_time"], "%H:%M:%S").strftime("%I:%M %p")
                        else:
                            hours = hours + " " + store_hours[i]["day_name"] + " Closed"
                    store.append(hours if hours != "" else "<MISSING>")
                    #print(store)
                    return_main_object.append(store)
                    break
                except:
                    continue
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
