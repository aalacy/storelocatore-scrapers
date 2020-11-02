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
    base_url = "https://drpilatesla.com"
    r = session.get(base_url)
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
    lcoations = soup.find("div",{"class":"section locations"})
    for location in lcoations.find_all("div",{"class":'column-2'}):
        name = location.find("h2").text
        lcoation_details = location.find_all('span')
        phone = lcoation_details[0].text.split("T:")[1]
        geo_location = location.find_all("a")[-1]['href']
        store = []
        store.append("https://drpilatesla.com")
        store.append(name)
        store.append(lcoation_details[1].text)
        store.append(lcoation_details[2].text.split(",")[0])
        store.append(lcoation_details[2].text.split(",")[-1])
        store.append(lcoation_details[3].text)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("dr pilates")
        store.append(geo_location.split("/@")[1].split(",")[0])
        store.append(geo_location.split("/@")[1].split(",")[1])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
