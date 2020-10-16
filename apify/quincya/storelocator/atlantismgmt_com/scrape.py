import csv
import time
from sgselenium import SgSelenium
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    driver = SgSelenium().chrome()
    time.sleep(2)

    base_link = 'http://www.atlantismgmt.com/store-locator/'
    
    driver.get(base_link)
    element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.ID, "storeLocator__storeList")))
    time.sleep(2)

    base = BeautifulSoup(driver.page_source,"lxml")

    locator_domain = "atlantismgmt.com"

    data = []
    items = base.find(id="storeLocator__storeList").find_all(class_="store-locator__infobox")

    for item in items:
        location_name = item.find(class_="infobox__row infobox__title store-location").text.strip()
        raw_address = item.find(class_="infobox__row store-address").text.strip().split("  ")
        street_address = raw_address[0].replace("11419","").strip()
        city_line = raw_address[1].replace(",","").strip()
        city = raw_address[1].replace(",","").strip()
        state = raw_address[-1].split()[0].strip()
        zip_code = raw_address[-1].split()[1].strip()
        country_code = "US"
        phone = "<MISSING>"
        store_number = location_name.split("#")[1]
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

        map_link = item.find(class_="infobox__row infobox__cta ssflinks")["href"]
        latitude = map_link.split("(")[-1].split(",")[0].strip()
        longitude = map_link.split("(")[-1].split(",")[1][:-1].strip()

        # Store data
        data.append([locator_domain, "<MISSING>", location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    driver.close()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
