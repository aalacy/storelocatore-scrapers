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
    base_url = "https://www.shopfuego.com"
    r = session.get("https://www.shopfuego.com/Store-Locator-s/105.htm",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for state in soup.find_all("td",{'colspan':"1","align":"center"}):
        link = state.find("a")["href"]
        if link[0] == "/":
            location_request = session.get(base_url + link)
        else:
            location_request = session.get(link)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        for location in location_soup.find("div",{'id':"content_area"}).find_all("div",{'class':"row"}):
            location_details = list(location.stripped_strings)
            geo_location = location.find("a")["href"]
            if len(location_details[3].split(" ")[-1]) == 5 and location_details[3].split(" ")[-1].isdigit():
                location_details[1] = " ".join(location_details[1:3])
                del location_details[2]
            store = []
            store.append("https://www.shopfuego.com")
            store.append(location_details[0].replace("\n"," "))
            store.append(location_details[1])
            store.append(location_details[2].split(",")[0])
            store.append(location_details[2].split(",")[1].split(" ")[1])
            store.append(location_details[2].split(",")[1].split(" ")[-1])
            store.append("US")
            store.append("<MISSING>")
            store.append(location_details[-1])
            store.append("fuego")
            store.append(geo_location.split("/@")[1].split(",")[0])
            store.append(geo_location.split("/@")[1].split(",")[1])
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
