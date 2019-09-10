import csv
import requests
from bs4 import BeautifulSoup
import re
import json

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
    base_url = "https://ferrari.com"
    r = requests.get("https://www.geocms.it/Server/servlet/S3JXServletCall?parameters=method_name%3DGetObject%26callback%3Dscube.geocms.GeoResponse.execute%26id%3D1%26idLayer%3DD%26query%3D%255BFilterDealer%255D%253D%255BY%255D%26licenza%3Dgeo-ferrarispa%26progetto%3DFerrari-Locator%26lang%3DALL&encoding=UTF-8",headers=headers)
    location_list = json.loads(json.loads(r.text.split("eval(scube.geocms.GeoResponse.execute(")[1].split('}",""')[0] + '}"'))["L"][0]["O"]
    return_main_object = []
    for location in location_list:
        if location['id'].isdigit() == False:
            continue
        location_request = requests.get("https://www.geocms.it/Server/servlet/S3JXServletCall?parameters=method_name%3DBalloonOnDemand%26callback%3Dscube.geocms.GeoResponse.execute%26id%3D3%26idLayer%3DD%26idObject%3D" + str(location["id"]) + "%26licenza%3Dgeo-ferrarispa%26progetto%3DFerrari-Locator%26lang%3DALL&encoding=UTF-8",headers=headers)
        store_data = json.loads(json.loads(location_request.text.split("eval(scube.geocms.GeoResponse.execute(")[1].split('}",""')[0] + '}"'))["L"][0]["O"][0]["U"]
        if store_data["Nation"] != "US" and store_data["Nation"] != "CA":
            continue
        store = []
        store.append("https://ferrari.com")
        store.append(store_data["Name"])
        if 'RoadNumber' in store_data:
            store.append(store_data["RoadNumber"] + "," + store_data["Address"])
        else:
            store.append(store_data["Address"])
        store.append(store_data["Locality"])
        store.append(store_data["ProvinceState"])
        store.append(store_data["Zipcode"])
        store.append(store_data["Nation"])
        store.append(location["id"])
        store.append(store_data["Telephone"])
        store.append("ferrari")
        store.append(store_data["Latitude"])
        store.append(store_data["Longitude"])
        hours = ""
        store_hours = store_data["G"]["Hours"][0]
        if "Mon-M-From" in store_hours:
            hours = hours + " Monday " + store_hours["Mon-M-From"] + " - " + store_hours["Mon-E-To"]
        else:
            hours = hours + " Monday " + " closed "
        if "Tue-M-From" in store_hours:
            hours = hours + " Tuesday " + store_hours["Tue-M-From"] + " - " + store_hours["Tue-E-To"]
        else:
            hours = hours + " Tuesday " + " closed "
        if "Wed-M-From" in store_hours:
            hours = hours + " Wednesday " + store_hours["Wed-M-From"] + " - " + store_hours["Wed-E-To"]
        else:
            hours = hours + " Wednesday " + " closed "
        if "Thu-M-From" in store_hours:
            hours = hours + " Thursday " + store_hours["Thu-M-From"] + " - " + store_hours["Thu-E-To"]
        else:
            hours = hours + " Thursday " + " closed "
        if "Fri-M-From" in store_hours:
            hours = hours + " Friday " + store_hours["Fri-M-From"] + " - " + store_hours["Fri-E-To"]
        else:
            hours = hours + " Friday " + " closed "
        if "Sat-M-From" in store_hours:
            hours = hours + " Saturday " + store_hours["Sat-M-From"] + " - " + store_hours["Sat-E-To"]
        else:
            hours = hours + " Saturday " + " closed "
        if "Sun-M-From" in store_hours:
            hours = hours + " Sunday " + store_hours["Sun-M-From"] + " - " + store_hours["Sun-E-To"]
        else:
            hours = hours + " Sunday " + " closed "
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
