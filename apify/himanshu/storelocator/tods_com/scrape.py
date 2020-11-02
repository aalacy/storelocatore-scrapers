import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.tods.com"
    r = session.get("https://www.geocms.it/Server/servlet/S3JXServletCall?parameters=method_name%3DGetObject%26callback%3Dscube.geocms.GeoResponse.execute%26id%3D5%26query%3D%255BcountryCode%255D%2520%253D%2520%255BUS%255D%26clear%3Dtrue%26licenza%3Dgeo-todsgroupspa%26progetto%3DTods%26lang%3DALL&encoding=UTF-8",headers=headers)
    return_main_object = []
    data = json.loads(json.loads(r.text.split("eval(scube.geocms.GeoResponse.execute(")[1].split(',"",')[0]))["L"][0]["O"]
    for store_data in data:
        store = []
        store.append("https://www.tods.com")
        store.append(store_data["U"]["name"])
        store.append(store_data["U"]['address'].split(store_data["U"]['region'])[0])
        store.append(store_data["U"]['city'])
        store.append(store_data["U"]['region'])
        store.append(store_data["U"]['zipCode'])
        store.append(store_data["U"]['countryCode'])
        store.append(store_data["U"]['shopCode'])
        store.append(store_data["U"]['phone'])
        store.append("tod's")
        store.append(store_data["G"][0]["P"][0]["y"])
        store.append(store_data["G"][0]["P"][0]["x"])
        days = {"1": "Monday","2":"Tuesday","3":"Wednesday","4":"Thursday","5":"Friday","6":"Saturday","7":"Sunday"}
        if "timeTable" in store_data["U"]:
            store.append(store_data["U"]["timeTable"])
        else:
            open_hours = store_data["U"]["G"]["hours"]
            try:
                hours = ""
                for k in range(len(open_hours)):
                    hours = hours + " " + days[open_hours[k]["day"]] + " from " + open_hours[k]["From1"] + "-" + open_hours[k]["To1"]
            except:
                hours = "<MISSING>"
            store.append(hours)
            store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
