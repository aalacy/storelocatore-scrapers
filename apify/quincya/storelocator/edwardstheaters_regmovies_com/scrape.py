import csv
import json
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

    base_link = 'https://www.regmovies.com/static/en/us/theatre-list'
    
    driver.get(base_link)
    time.sleep(8)

    base = BeautifulSoup(driver.page_source,"lxml")

    all_scripts = base.find_all('script')
    for script in all_scripts:
        if "latitude" in str(script):
            script = script.text.replace('\n', '').replace('\\', '').strip()
            break

    js = script.split("window.apiSitesList =")[-1].split("window.selectedLangParam")[0].strip()[:-1]
    stores = json.loads(js)

    data = []
    locator_domain = "regmovies.com"
    phone = "<MISSING>"
    for store in stores:
        location_name = store["name"]
        if "edwards" not in str(store).lower():
            continue
        street_address = store["address"]['address1']
        city = store["address"]['city']
        state = store["address"]["state"]
        zip_code = store["address"]['postalCode']
        country_code = "US"
        store_number = store["externalCode"]
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = store['latitude']
        longitude = store['longitude']
        link = "https://www.regmovies.com" + store['uri'] + "/" +  store_number
        # print(link)
        if phone != "(844) 462-7342":
            driver.get(link)
            element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
                (By.ID, "tab_getting-here")))
            time.sleep(2)
            base = BeautifulSoup(driver.page_source,"lxml")
            phone = base.find(id="tab_getting-here").find_all("span")[-1].text.strip()

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    driver.close()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
