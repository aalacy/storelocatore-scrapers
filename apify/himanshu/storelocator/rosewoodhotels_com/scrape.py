import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rosewoodhotels_com')




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
    base_url = "https://www.rosewoodhotels.com"
    r = session.get("https://www.rosewoodhotels.com/en/luxury-hotels-and-resorts",headers=headers)
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
    for link in soup.find("section",{"id":"us-and-canada"}).find_all("a"):
        logger.info(link["href"])
        location_request = session.get(base_url + link["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        if location_soup.find("p",{"class":"reservation-p"}) == None:
            continue
        location_details = list(location_soup.find("p",{"class":"reservation-p"}).stripped_strings)
        store = []
        store.append("https://www.rosewoodhotels.com")
        store.append(link.text)
        if "USA" in location_details:
            store.append(location_details[0])
            store.append(location_details[2])
            store.append(location_details[4])
            store.append(location_details[5])
            store.append("US")
        elif "Canada" in location_details:
            store.append(location_details[0])
            store.append(location_details[2])
            store.append(location_details[4])
            store.append(location_details[7])
            store.append("CA")
        elif "USA" in location_details[2]:
            store.append(" ".join(location_details[0:2]) + location_details[2].split(",")[0])
            store.append(location_details[2].split(",")[1])
            store.append(location_details[2].split(",")[2].split(" ")[1])
            store.append(location_details[2].split(",")[2].split(" ")[-1])
            store.append("US")
        else:
            store.append(location_details[0].split(",")[0])
            store.append(location_details[0].split(",")[1])
            store.append(location_details[0].split(",")[2].split(" ")[1])
            store.append(location_details[0].split(",")[2].split(" ")[-1].replace("\xa0","").replace("|",""))
            store.append("US")
        store.append("<MISSING>")
        store.append(location_details[-1])
        store.append("rose wood")
        if location_soup.find("a",{"class":"inline-a location bold gtm-footer"}) == None:
            store.append("<MISSING>")
            store.append("<MISSING>")
        else:
            geo_request = session.get(base_url + location_soup.find("a",{"class":"inline-a location bold gtm-footer"})["href"])
            geo_soup = BeautifulSoup(geo_request.text,"lxml")
            geo_location = geo_soup.find("div",{"class":"locmap"})["data-ll"]
            store.append(geo_location.split(",")[1])
            store.append(geo_location.split(",")[0])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
