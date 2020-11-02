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
    base_url = "https://www.vineyardvines.com"
    r = session.get("https://www.vineyardvines.com/stores",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("a"):
        if "/storedetails?StoreID=" not in location["href"]:
            continue
        location_request = session.get("https://www.vineyardvines.com" + location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("h2",{"class":"storedetail_name"}).text
        phone = location_soup.find("p",{"itemprop":"telephone"}).find("a")["href"].split("tel:")[1].replace("\u200b","")
        address = list(location_soup.find("ul",{"class":"storedetail_address"}).stripped_strings)
        store_hours = location_soup.find_all("span",{"itemprop":"openingHours"})
        hours = ""
        for i in range(len(store_hours)):
            hours = hours + " ".join(list(store_hours[i].stripped_strings)) + " "
        store = []
        store.append("https://www.vineyardvines.com")
        store.append(name)
        store.append(address[0].replace("\n"," "))
        store.append(address[-1].split(",")[0])
        if len(address[-1].split(",")[1].split(" ")) < 3:
            store.append(address[-1].split(",")[1].split(" ")[-1])
            store.append("<MISSING>")
        else:
            store.append(address[-1].split(",")[1].split(" ")[-2])
            store.append(address[-1].split(",")[1].split(" ")[-1])
        if len(store[-1]) < 5:
            continue
        store.append("US")
        store.append(location["href"].split("=")[1])
        store.append(phone if phone != "null" else "<MISSING>")
        store.append("vineyard vines")
        store.append(location_soup.find("a",{"id":"getdirections"})["href"].split("&sll=")[1].split(",")[0].strip())
        store.append(location_soup.find("a",{"id":"getdirections"})["href"].split("&sll=")[1].split(",")[1].split("&")[0].strip())
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
