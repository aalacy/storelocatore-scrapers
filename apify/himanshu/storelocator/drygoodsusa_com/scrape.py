import csv
import os
import requests
from sgselenium import SgSelenium 
import re
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('drygoodsusa_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    driver = SgSelenium().firefox()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    addresses = []
    base_url = "https://www.drygoodsusa.com"

    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    page_url = ""

    driver.get('https://www.drygoodsusa.com/Stores.aspx')
    soup = BeautifulSoup(driver.page_source,"lxml")
    # logger.info("soup === "+str(soup))

    for script in soup.find_all("div", {"class": "divStoresListStore"}):
        page_url = base_url+"/"+script.find("a")["href"]
        # logger.info("liunk ==== "+ page_url)
        driver.get(page_url)
        # logger.info("driver.page_source ==== " + str(driver.page_source))
        soup_location = BeautifulSoup(driver.page_source, "lxml")
        location_name = soup_location.find("div",{"class":"divStoresTitle"}).text
        full_address = list(soup_location.find("div",{"class":"divStoreInfoBox"}).stripped_strings)
        street_address = full_address[0]

        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(full_address))
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address[1]))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address[1]))
        state_list = re.findall(r' ([A-Z]{2}) ', full_address[1])

        phone = ""
        state = ""
        zipp = ""

        if phone_list:
            phone = phone_list[0]

        if ca_zip_list:
            zipp = ca_zip_list[0]
            country_code = "CA"

        if us_zip_list:
            zipp = us_zip_list[0]
            country_code = "US"

        if state_list:
            state = state_list[0]

        city = full_address[1].replace(zipp, "").replace(state, "").replace(",", "")

        latitude = soup_location.text.split("new google.maps.LatLng(")[1].split(",")[0]
        longitude = soup_location.text.split("new google.maps.LatLng(")[1].split(",")[1].split(")")[0]

        # logger.info("soup_location -==== "+ str(full_address))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[1]) + str(store[2]) not in addresses:
            addresses.append(str(store[1]) + str(store[2]))

            store = [x.strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
