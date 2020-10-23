import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('elpatomexicanfood_com')




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
    base_url = "https://elpatomexicanfood.com"
    r = session.get("https://elpatomexicanfood.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    hours = " ".join(list(soup.find("div",{"class":"et_pb_row et_pb_row_5"}).find("div",{"class":'et_pb_text_inner'}).stripped_strings))
    for link in soup.find_all("a",text=re.compile("View Location")):
        logger.info(link["href"])
        location_request = session.get(link["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find_all("div",{"class":re.compile("et_pb_module et_pb_text")})[0:2][0].text.strip()
        address = location_soup.find_all("div",{"class":re.compile("et_pb_module et_pb_text")})[0:2][1].text.strip().split("•")
        store = []
        store.append("https://elpatomexicanfood.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0] if len(address) == 3 else "<MISSING>")
        store.append(address[1].split(",")[1].split(" ")[1] if len(address) == 3 else "<MISSING>")
        store.append(address[1].split(",")[1].split(" ")[-2] if len(address) == 3 else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(address[-1])
        store.append("el pato")
        if location_soup.find("a",{"href":re.compile("/@")}) == None:
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
        else:
            geo_location = location_soup.find("a",{"href":re.compile("/@")})["href"]
            lat = geo_location.split("/@")[1].split(",")[0]
            lng = geo_location.split("/@")[1].split(",")[1]
            store.append(lat)
            store.append(lng)
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
