import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    cords = sgzip.coords_for_radius(100)
    return_main_object = []
    addresses = []
    for cord in cords:
        base_url = "https://www.aveda.com"
        data = 'JSONRPC=%5B%7B%22method%22%3A%22locator.doorsandevents%22%2C%22id%22%3A7%2C%22params%22%3A%5B%7B%22fields%22%3A%22DOOR_ID%2C+SALON_ID%2C+ACTUAL_DOORNAME%2C+ACTUAL_ADDRESS%2C+ACTUAL_ADDRESS2%2C+ACTUAL_CITY%2C+STORE_TYPE%2C+STATE%2C+ZIP%2C+DOORNAME%2C+ADDRESS%2C+ADDRESS2%2C+CITY%2C+STATE_OR_PROVINCE%2C+ZIP_OR_POSTAL%2C+COUNTRY%2C+PHONE1%2C+CLASSIFICATION%2C+IS_SALON%2C+IS_LIFESTYLE_SALON%2C+IS_INSTITUTE%2C+IS_FAMILY_SALON%2C+IS_CONCEPT_SALON%2C+IS_STORE%2C+HAS_EXCLUSIVE_HAIR_COLOR%2C+HAS_PURE_PRIVILEGE%2C+HAS_PERSONAL_BLENDS%2C+HAS_GIFT_CARDS%2C+HAS_PAGE%2C+HAS_SPA_SERVICES%2C+IS_GREEN_SALON%2C+HAS_RITUALS%2C+DO_NOT_REFER%2C+HAS_EVENTS%2C+LONGITUDE%2C+LATITUDE%2C+LOCATION%2C+WEBURL%2C+EMAILADDRESS%2C+APPT_URL%22%2C%22radius%22%3A%22100%22%2C%22country%22%3A%22USA%22%2C%22city%22%3A%22USA%22%2C%22region_id%22%3A%220%22%2C%22language_id%22%3A%22%22%2C%22latitude%22%3A' + str(cord[0]) + '%2C%22longitude%22%3A' + str(cord[1]) + '%2C%22uom%22%3A%22miles%22%2C%22primary_filter%22%3A%22filter_salon_spa_store%22%2C%22filter_HC%22%3A0%2C%22filter_PP%22%3A0%2C%22filter_SS%22%3A0%2C%22filter_SR%22%3A0%2C%22filter_EM%22%3A0%7D%5D%7D%5D'
        r = session.post("https://www.aveda.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents",headers=headers,data=data)
        data = r.json()[0]["result"]["value"]["results"]
        for key in data:
            store_data = data[key]
            if store_data["COUNTRY"] != "USA" and store_data["COUNTRY"] != "Canada":
                continue
            store = []
            store.append("https://www.aveda.com")
            store.append(store_data["DOORNAME"])
            store.append(store_data["ADDRESS"] + " " + store_data["ADDRESS2"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["CITY"])
            store.append(store_data["STATE_OR_PROVINCE"])
            store.append(store_data["ZIP_OR_POSTAL"])
            store.append("US" if store_data["COUNTRY"] == "USA" else "CA")
            store.append(key)
            store.append(store_data["PHONE1"] if store_data["PHONE1"] != "" and store_data["PHONE1"] != None else "<MISSING>")
            store.append("aveda")
            store.append(store_data["LATITUDE"])
            store.append(store_data["LONGITUDE"])
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
