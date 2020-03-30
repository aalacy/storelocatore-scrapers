import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    base_url = "https://www.oktire.com"
    data = 'action=api_oktire_stores&path=search&filter%5Bkeywords%5D=&filter%5Bcity%5D=&filter%5Bzip%5D=&filter%5Bcountry%5D=&filter%5Bloc%5D=56.130366%2C-106.34677099999999&filter%5Bradius%5D=99999&filter%5Bcommercial%5D=0'
    r = session.post("https://www.oktire.com/wp-admin/admin-ajax.php",headers=headers,data=data)
    return_main_object = []
    location_list = r.json()["items"]
    for i in range(len(location_list)):
            store_data = location_list[i]
            store = []
            store.append("https://www.oktire.com")
            store.append(store_data["name"])
            store.append(store_data["street"])
            store.append(store_data["City"])
            store.append(store_data["StateProvince"])
            store.append(store_data["ZIPPostal_Code"] if len(store_data["ZIPPostal_Code"]) != 6 else store_data["ZIPPostal_Code"][0:3] + " " + store_data["ZIPPostal_Code"][3:])
            store.append("CA")
            store.append(store_data["id"])
            store.append(store_data["phone"]["formatted"] if store_data["phone"]["formatted"]  != "" else "<MISSING>")
            store.append("<MISSING>")
            store.append(store_data["Latitude"])
            store.append(store_data["Longitude"])
            hours = ""
            store_hours = store_data["hours"]
            for key in store_hours:
                hours = hours + " " + store_hours[key]["label"] + " " + store_hours[key]["hours"]
            store.append(hours if hours  != "" else "<MISSING>")
            store.append("<MISSING>")
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
