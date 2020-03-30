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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    }
    base_url = "https://www.panago.com"
    r = session.get("https://assets-cdn.scdn4.secure.raxcdn.com/static_assets/js/bundle-46119c59a24c18fd7bdd.js",headers=headers)
    token = r.text.split("webToken")[1].split(",")[0].split(':"')[1].split('"')[0]
    city_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        "Origin": "https://www.panago.com",
        "Referer": "https://www.panago.com/locations",
        "Accept": "application/vnd.panago_api.v1",
        "Content-Type": "application/json",
        "Authorization": 'Token token="'+ token + '"'
    }
    data = '{"store_number":918}'
    city_request = session.post("https://api.panagopos.com/locations",headers=city_headers,data=data)
    locations = city_request.json()["data"]["locations"]
    store_ids = []
    return_main_object = []
    location_token = city_request.headers["Access-Token"]
    for i in range(len(locations)):
        location_city = locations[i]["province_cities"]
        for k in range(len(location_city)):
            city = location_city[k]
            location_headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
                "Origin": "https://www.panago.com",
                "Referer": "https://www.panago.com/locations",
                "Accept": "application/vnd.panago_api.v1",
                "Content-Type": "application/json",
                "Authorization": 'Token token="'+ location_token + '"'
            }
            location_data = '{"search_params":{"query":"' + city + '"}}'
            location_request = session.post("https://api.panagopos.com/stores/search",headers=location_headers,data=location_data)
            data = location_request.json()["data"]
            for i in range(len(data)):
                store_data = data[i]
                store = []
                store.append("https://www.panago.com")
                store.append("<MISSING>")
                store.append(store_data["address"])
                store.append(store_data["city"]["name"])
                store.append(store_data["province_code"])
                store.append(store_data["postal_code"])
                store.append("CA")
                if store_data["store_number"] in store_ids:
                    continue
                store_ids.append(store_data["store_number"])
                store.append(store_data["store_number"])
                store.append(store_data["phone"])
                store.append("<MISSING>")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                store.append(store_data["hours"].replace("\n",""))
                store.append("<MISSING>")
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
