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
    base_url = "https://www.zoup.com"
    r = session.get("https://www.zoup.com/ajax.Location.php?action=initialize",headers=headers)
    state_data = r.json()[3]
    return_main_object = []
    store_ids = []
    for key in state_data:
        city = state_data[key]
        for i in range(len(city)):
            for k in range(len(city[i])):
                location_request = session.get("https://www.zoup.com/ajax.Location.php?action=locations&zipcode=&state="+ key +"&city=" + city[i][k],headers=headers)
                data = location_request.json()
                for j in range(len(data)):
                    for l in range(len(data[j])):
                        store_data = data[j][l]
                        store = []
                        store.append("https://www.zoup.com")
                        store.append(store_data["companyname"])
                        store.append(BeautifulSoup((store_data["address1"] + store_data["address2"] + store_data["address3"]),"lxml").get_text())
                        store.append(store_data["city"])
                        store.append(store_data["state"])
                        if len(store_data["zip"]) == 5:
                            store.append(store_data["zip"])
                            store.append("US")
                        else:
                            if len(store_data["zip"]) == 6:
                                store.append(store_data["zip"][0:3] + " " + store_data["zip"][3:])
                                store.append("CA")
                            else:
                                store.append(store_data["zip"])
                                store.append("CA")
                        store.append(store_data["id"])
                        if store_data["id"] in store_ids:
                            continue
                        store_ids.append(store_data["id"])
                        store.append(store_data["phonenumber"])
                        store.append("zoup")
                        store.append(store_data["latitude"])
                        store.append(store_data["longitude"])
                        store.append(BeautifulSoup(store_data["hours"],"lxml").get_text())
                        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
