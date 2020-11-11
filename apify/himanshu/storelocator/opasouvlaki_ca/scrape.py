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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://opasouvlaki.ca"
    r = session.get("https://opasouvlaki.ca/wp-json/opasouvlaki/v1/search-locations/11756",headers=headers)
    data = r.json()
    return_main_object = []
    for store_data in data:
        store = []
        store.append("https://opasouvlaki.ca")
        store.append(store_data['location'])
        store.append(store_data["address"])
        store.append(store_data['city'])
        try:
            store.append(store_data['province'])
        except KeyError:
            store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("US" if int(store_data["latitude"].split(".")[0]) < 39 else "CA")
        store.append(store_data["id"])
        store.append(store_data["phone"])
        store.append("opa of greece")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        hours = ""
        try:
            hours = hours + " monday " + store_data["monday"]["open"] + " - " + store_data["monday"]["close"]
        except:
            hours = hours + " monday Closed"
        try:
            hours = hours + " tuesday " + store_data["tuesday"]["open"] + " - " + store_data["tuesday"]["close"]
        except:
            hours = hours + " tuesday Closed"
        try:
            hours = hours + " wednesday " + store_data["wednesday"]["open"] + " - " + store_data["wednesday"]["close"]
        except:
            hours = hours + " wednesday Closed"
        try:
            hours = hours + " thursday " + store_data["thursday"]["open"] + " - " + store_data["thursday"]["close"]
        except:
            hours = hours + " thursday  Closed"
        try:
            hours = hours + " friday " + store_data["friday"]["open"] + " - " + store_data["friday"]["close"]
        except:
            hours = hours + " friday Closed"
        try:
            hours = hours + " saturday " + store_data["saturday"]["open"] + " - " + store_data["saturday"]["close"]
        except:
            hours = hours + " saturday Closed"
        try:
            hours = hours + " sunday " + store_data["sunday"]["open"] + " - " + store_data["sunday"]["close"]
        except:
            hours = hours + " sunday Closed"
        store.append(hours if hours != "" else "<MISSING>")
        store.append("<MISSING>")
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
