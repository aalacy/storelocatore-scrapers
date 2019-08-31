import csv
import requests
from bs4 import BeautifulSoup
import re
import json

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
    base_url = "https://www.uwmedicine.org"
    r = requests.get("https://www.uwmedicine.org/search/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("article",{"role":'article'}):
        link = location.find("a")["href"]
        location_request = requests.get(link,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("h1",{"class":"page-title"}).text.strip()
        phone = location_soup.find("a",{"href":re.compile("tel:")}).text
        hours = location_soup.find("div",{"id":"clinic-hours-operation-details"}).text.strip()
        address = list(location_soup.find("div",{"class":"clinic-card__street-address"}).stripped_strings)
        store = []
        store.append("https://www.uwmedicine.org")
        store.append(name)
        store.append(address[0].replace(",",""))
        store.append(address[1].replace(",",""))
        store.append(address[2].replace(",",""))
        store.append(address[3].replace(",",""))
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("UW Medicine")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
