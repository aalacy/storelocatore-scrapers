import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
import time

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
    r = session.get("http://www.winotstop.com/locations.html")
    soup = BeautifulSoup(r.text,"lxml")
    iframe_link = soup.find("iframe")["src"]
    r = session.get(iframe_link)
    soup = BeautifulSoup(r.text,"lxml")
    geo_location = {}
    for script in soup.find_all("script"):
        if "_pageData" in script.text:
            location_list = json.loads(script.text.split('var _pageData = "')[1].split('\n";')[0].replace('\\"','"').replace(r"\n","")[:-2].replace("\\"," "))[1][6][0][12][0][13][0]
            for location in location_list:
                geo_location[location[5][0][1][0]] = location[1][0][0]
    driver = SgSelenium().firefox()
    addresses = []
    base_url = "https://www.trumphotels.com/"
    driver.get(iframe_link)
    for button in driver.find_elements_by_xpath("//img[@src='https://mt.googleapis.com/vt/icon/name=icons/onion/SHARED-mymaps-pin-container-bg_4x.png,icons/onion/SHARED-mymaps-pin-container_4x.png,icons/onion/1899-blank-shape_pin_4x.png&highlight=ff000000,0288D1&scale=2.0']"):
        try:
            button.click()
            time.sleep(1)
            location_soup = BeautifulSoup(driver.page_source, "lxml")
            address = list(location_soup.find("div",text=re.compile("Details from Google Maps")).parent.stripped_strings)[1]
            if len(address.split(",")) == 2:
                street_address = "<MISSING>"
                city = address.split(",")[0]
            else:
                street_address = address.split(",")[0]
                city = address.split(",")[1]
            store_zip_split = re.findall("([0-9]{5})",address)
            if store_zip_split:
                store_zip = store_zip_split[-1]
            else:
                store_zip = "<MISSING>"
            state_split = re.findall("([A-Z]{2})",address)
            if state_split:
                state = state_split[-1]
            else:
                state = "<MISSING>"
            name = list(location_soup.find("div",text=re.compile("name")).parent.stripped_strings)[1]
            phone = list(location_soup.find("div",text=re.compile("description")).parent.stripped_strings)[2].replace("Phone","").replace("\t","")
            store = []
            store.append("http://www.winotstop.com")
            store.append(name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(store_zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(geo_location[name][0])
            store.append(geo_location[name][1])
            store.append("<MISSING>")
            yield store
        except:
            time.sleep(1)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
