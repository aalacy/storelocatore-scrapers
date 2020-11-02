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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.altierus.edu"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("div",{"class":"section campuses"}).find_all("li"):
        link = location.find("a")['href']
        location_request = session.get(base_url + link)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = list(location_soup.find("div",{"class": "deck campus"}).stripped_strings)[0]
        location_address = list(location_soup.find("div",{"itemprop": "address"}).stripped_strings)
        phone = location_soup.find("span",{"itemprop": "telephone"}).text
        hours = ' '.join(list(location_soup.find("div",{"class": "hours"}).stripped_strings))
        store = []
        store.append("https://www.altierus.edu")
        store.append(name)
        store.append(location_address[0])
        store.append(location_address[1])
        store.append(location_address[3])
        store.append(location_address[4])
        store.append("US")  
        store.append("<MISSING>")
        store.append(phone)
        store.append("altierus")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
