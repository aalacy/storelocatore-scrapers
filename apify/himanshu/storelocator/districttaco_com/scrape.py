import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Firefox(options=options,executable_path="./geckodriver")

def fetch_data():
    driver = get_driver()
    driver.get("https://www.districttaco.com/pages/locations")
    driver.find_element_by_xpath("//button[@id='ListView']").click()
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source,"lxml")
    hours_object = {}
    for location in soup.find_all("div",{"class":"grid__item medium-up--one-third"}):
        address  = list(location.find("span").stripped_strings)
        name = location.find("strong").text.strip()
        hours = " ".join(list(location.find("table").stripped_strings))
        hours_object[name] = ["-".join(address),hours]
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.districttaco.com"
    r = requests.get("https://www.districttaco.com/pages/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    geo_locations = []
    for script in soup.find_all("script"):
        if "function initMap() {" in script.text:
            geo = script.text.split("lat: ")[1:]
            for lat in geo:
                geo_locations.append([lat.split(",")[0],lat.split("lng: ")[1].split("}")[0]])
        if "openingHours" in script.text:
            location_list = json.loads(script.text)["location"]
    for i in range(len(location_list)):
        store_data = location_list[i]
        store = []
        store.append("https://www.districttaco.com")
        store.append(store_data["name"])
        for key in hours_object:
            if store[1].replace(" District Taco ","") in key:
                store.append("-".join(hours_object[key][0].split("-")[:-1]))
                break
        if len(store) == 2:
            for key in hours_object:
                if store_data["address"]["addressLocality"] in hours_object[key][0]:
                    store.append("-".join(hours_object[key][0].split("-")[:-1]))
                    break
        store.append(store_data["address"]["addressLocality"])
        store.append(store_data["address"]["addressRegion"])
        store.append(store_data["address"]["postalCode"])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["telephone"])
        store.append("<MISSING>")
        store.append(geo_locations[i][0])
        store.append(geo_locations[i][1])
        for key in hours_object:
            if store[1].replace(" District Taco ","") in key:
                    store.append(hours_object[key][1])
                    break
        if len(store) == 12:
            for key in hours_object:
                if store_data["address"]["addressLocality"] in hours_object[key][0]:
                    store.append(hours_object[key][1])
                    break
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
