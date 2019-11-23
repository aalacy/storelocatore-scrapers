import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import platform

system = platform.system()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    if "linux" in system.lower():
        return webdriver.Firefox(options=options,executable_path="./geckodriver")
    else:
        return webdriver.Firefox(executable_path='geckodriver.exe', options=options)
def fetch_data():
    addresses = []
    driver = get_driver()
    driver.get("https://www.odfl.com/ServiceCenterLocator/locator.faces")
    states = []
    for button in driver.find_elements_by_xpath("//select[@name='locatorForm:j_idt40']/option"):
        state = button.get_attribute("value")
        if len(state) != 2:
            continue
        states.append(state)
    for state in states:
        element = WebDriverWait(driver, 100).until(lambda x: x.find_element_by_xpath("//option[@value='" + state + "']"))
        driver.find_element_by_xpath("//option[@value='" + state + "']").click()
        driver.find_element_by_xpath("//input[@name='locatorForm:j_idt44']").click()
        try:
            element = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath("//li[@style='color:red; display:block']"))
            continue
        except:
            pass
        element = WebDriverWait(driver, 100).until(lambda x: x.find_element_by_xpath("//input[@value='Return']"))
        soup = BeautifulSoup(driver.page_source,"lxml")
        for location in soup.find("table",{"border":"4"}).find_all("td"):
            name = location.find("h4").text.strip()
            address = list(location.stripped_strings)[1]
            phone = list(location.stripped_strings)[2]
            zip_split = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',address)
            country = ""
            if zip_split:
                store_zip = zip_split[-1]
                if len(store_zip) == 6:
                    store_zip = store_zip[:3] + " " + store_zip[3:]
                country = "CA"
            else:
                zip_split =  re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",address)
                store_zip = zip_split[-1]
                country = "US"
            state_split = re.findall("([A-Z]{2})",address)
            if state_split:
                state = state_split[-1]
            else:
                state = "<MISSING>"
            store = []
            store.append("https://www.odfl.com")
            store.append(name)
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append(state)
            store.append(store_zip)
            store.append(country)
            store.append("<MISSING>")
            store.append(phone.split(":")[1] if "Phone" in phone else "<MISSING>")
            store.append("<MISSING>") # location type
            store.append("<MISSING>") # lat
            store.append("<MISSING>") # lng
            store.append("<MISSING>") # hours
            store.append("<MISSING>") # page_url
            store.append(address.replace(state,"").replace(store_zip,"").replace(",",""))
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            yield store
        driver.find_element_by_xpath("//input[@value='Return']").click()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()