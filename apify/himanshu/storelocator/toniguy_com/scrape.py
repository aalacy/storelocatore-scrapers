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
    base_url = "https://toniguy.com"
    r = session.get("https://salons.toniguy.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []

    scripts = soup.find_all("script")
    return_main_object = []
    for script in scripts:
        if "window.LOCATIONS = " in script.text:
            location_list = json.loads(script.text.split("window.LOCATIONS = ")[1].split("}];")[0] + "}]")
            for i in range(len(location_list)):
                current_store = location_list[i]
                location_request = session.get("https://" +current_store["url"])
                location_soup = BeautifulSoup(location_request.text,"lxml")
                address = list(location_soup.find("div",{"class":"address-info"}).stripped_strings)
                if location_soup.find("a",{"class":"phone"}) == None:
                    phone = "<MISSING>"
                else:
                    phone = location_soup.find("a",{"class":"phone"}).text
                hours = " ".join(list(location_soup.find("div",{"class":'hours'}).stripped_strings))
                name = location_soup.find("h1").text
                store = []
                store.append("https://toniguy.com")
                store.append(name)
                store.append(" ".join(address[:-1]))
                store.append(address[-1].split(",")[0])
                store.append(address[-1].split(",")[1].split(" ")[1])
                if len(address[-1].split(",")[1].split(" ")[-1]) == 3:
                    store.append(" ".join(address[-1].split(",")[1].split(" ")[2:]))
                    store.append("CA")
                else:
                    store.append(address[-1].split(",")[1].split(" ")[-1])
                    store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("tony and guy")
                store.append(current_store["lat"])
                store.append(current_store["lng"])
                store.append(hours)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
