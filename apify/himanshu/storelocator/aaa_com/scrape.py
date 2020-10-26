import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('aaa_com')




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
    return_main_object = []
    r = session.get("https://branches.northeast.aaa.com/api/v1/branches/locations")
    data = r.json()
    for i in range(len(data)):
        location_url = BeautifulSoup(data[i]["popupHtml"],"lxml").find("a")["href"]
        location_request = session.get(location_url)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = data[i]["name"]
        logger.info(name)
        location_address = list(location_soup.find("div",{"class":"aaa-branch-address"}).stripped_strings)
        phone = location_soup.find("a",{"class":"aaa-branch-phone"}).text
        hours = list(location_soup.find("div",{"class":"aaa-branch-hours"}).stripped_strings)
        store = []
        store.append("https://www.aaa.com")
        store.append(name)
        store.append(location_address[0])
        store.append(location_address[1].split(",")[0])
        store.append(location_address[1].split(",")[1].split(" ")[-2])
        store.append(location_address[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("aaa")
        store.append(data[i]["latitude"])
        store.append(data[i]["longitude"])
        store.append(" ".join(hours))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
