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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.cobsbread.com"
    r = session.get("https://www.cobsbread.com/local-bakery/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "var bakeries = " in script.text:
            location_list = json.loads(script.text.split("var bakeries = ")[1].split("}],")[0] + "}]")
            for store_data in location_list:
                location_request = session.get(store_data["link"],headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                address = list(location_soup.find("p",{'class':"trailer--none"}).stripped_strings)
                if len(address) < 3:
                    continue
                phone = location_soup.find("a",{'class':"single-bakery__phone"}).text.strip()
                hours = " ".join(list(location_soup.find("div",{'class':"bakery-hours"}).stripped_strings))
                store = []
                store.append("https://www.cobsbread.com")
                store.append(store_data["title"])
                store.append(address[0])
                store.append(address[1].split(",")[0])
                store.append(address[1].split(",")[1])
                store.append(address[2])
                store.append("US" if len(address[2]) == 5 else "CA")
                if store[-1] == "CA":
                    if len(store[-2]) == 6:
                        store[-2] = store[-2][0:3] + " " + store[-2][3:]
                if len(store[-2]) == 4:
                    store[-1] == "US"
                store.append("<MISSING>")
                store.append(phone.replace("\u202c","") if phone != "" else "<MISSING>")
                store.append("cobs bread")
                store.append(store_data["map_data"]["lat"] if store_data["map_data"] != "" else "<MISSING>")
                store.append(store_data["map_data"]["lng"] if store_data["map_data"] != "" else "<MISSING>")
                store.append(hours)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
