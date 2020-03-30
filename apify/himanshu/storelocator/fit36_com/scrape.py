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
    base_url = "https://fit36.com"
    r = session.get("https://fit36.com/js/maps.js",headers=headers)
    token = r.text.split("accessToken = ")[1].split(";")[0].replace("'","")
    main_request = session.get("https://fit36.com/find-a-studio",headers=headers)
    main_soup = BeautifulSoup(main_request.text,"lxml")
    return_main_object = []
    for location in main_soup.find_all(lambda tag: tag.name == 'a' and tag.get('class') == ['abbr']):
        location_geo_request = session.get("https://api.mapbox.com/geocoding/v5/mapbox.places/" + location["href"].split("?q=")[1] + ".json/?access_token="+ token + "&country=US%2CCA&types=region%2Cpostcode%2Cplace",headers=headers)
        geo_cord = location_geo_request.json()["features"][0]["center"]
        location_request = session.get(("https://fit36.com/locator?q=" + location["href"].split("?q=")[1] + "&lat=" + str(geo_cord[1]) + "&lng="+ str(geo_cord[0]) +"&limit=50").replace("State,",""),headers=headers)
        location_list = location_request.json()["locations"]
        for i in range(len(location_list)):
            store_data = location_list[i]
            store = []
            store.append("https://fit36.com")
            store.append(store_data["name"])
            store.append(store_data["address"] + " " + store_data["address_2"])
            store.append(store_data["city"])
            store.append(store_data["state"])
            store.append(store_data["zip_code"])
            store.append("US")
            store.append(store_data["id"])
            store.append(store_data["phone_number"])
            store.append("fit 36")
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            hours = ""
            if store_data["hours_of_operation"] != False:
                for key in store_data["hours_of_operation"]:
                    hours = hours + " " + key + " " + store_data["hours_of_operation"][key]
            store.append(hours if hours != "" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
