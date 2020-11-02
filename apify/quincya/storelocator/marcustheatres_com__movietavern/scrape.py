import csv
import json
import time
from sgselenium import SgSelenium
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="marcustheatres.com")


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    driver = SgSelenium().chrome()
    time.sleep(2)

    base_link = 'https://www.marcustheatres.com/theatre-locations/theatre-search/?Brand=Movie+Tavern'
    
    driver.get(base_link)
    element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.CLASS_NAME, "theatre-name")))
    time.sleep(2)

    base = BeautifulSoup(driver.page_source,"lxml")

    locator_domain = "marcustheatres.com"

    data = []
    items = base.find_all(class_="theatre-name")

    for item in items:
        link = "https://www.marcustheatres.com" + item.a["href"]
        log.info(link)
        driver.get(link)
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "aside-content")))
        time.sleep(2)
        base = BeautifulSoup(driver.page_source,"lxml")

        location_name = base.h1.text.strip()

        raw_address = base.find(class_="aside-content").a.text.strip().split("\n")
        street_address = raw_address[0].strip()
        city_line = raw_address[1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[1].split()[0].strip()
        zip_code = city_line[1].split()[1].strip()
        country_code = "US"
        phone = base.find(class_="theatre-map__box-office-phone").text.strip()
        store_number = "<MISSING>"
        desc = base.find(class_="theatre-info__description").text.lower()
        if "temporarily closed" in desc:
            location_type = "Temporarily Closed"
        else:
            location_type = "Open"
        hours_of_operation = "<MISSING>"

        map_link = base.find(class_="aside-content").a["href"]
        latitude = map_link.split(":")[-1].split("+")[0]
        longitude = map_link.split(":")[-1].split("+")[1]

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    driver.close()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
