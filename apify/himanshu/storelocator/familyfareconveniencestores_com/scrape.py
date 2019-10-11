import csv

import requests
from bs4 import BeautifulSoup
import re
import json
import urllib.parse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from selenium.webdriver.support.wait import WebDriverWait


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Firefox(executable_path='./geckodriver', options=options)


def fetch_data():
    # print("start")

    base_url = "https://www.familyfareconveniencestores.com"

    addresses = []
    driver = get_driver()
    driver.get("http://familyfareconveniencestores.com/Locations/")
    cities = []

    # driver.find_element_by_xpath("//select[@name='selStates']").click()

    for button in driver.find_elements_by_xpath("//select[@name='ctl00$LeftNavigation$CommunityDDL$CityDDL']/option"):
        city = button.get_attribute("value")
        # print("city === " + city)
        if len(city) != 2:
            continue
        cities.append(city)

    for city in cities:
        driver.find_element_by_xpath("//select[@name='ctl00$LeftNavigation$CommunityDDL$CityDDL']").click()
        driver.find_element_by_xpath("//option[@value='" + city + "']").click()
        # WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath("//option[@value='']"))  # wait until data

        list_a = []
        for a_tag in driver.find_elements_by_xpath("//a[contains(@id,'MainContent_ResultsGridView_LocationHL')]"):
            list_a.append(a_tag.get_attribute("id"))

        for location in list_a:

            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            city = ""
            zipp = ""
            state = ''
            country_code = "US"
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            raw_address = ""
            hours_of_operation = ""
            page_url = ""

            address_soup = BeautifulSoup(driver.page_source,"lxml")
            full_address = list(address_soup.find("a",{"id":location}).stripped_strings)
            location_name = full_address[0]
            street_address = full_address[-2]
            city = full_address[-1]
            driver.find_element_by_xpath("//a[@id='"+location+"']").click()
            page_url = driver.current_url

            # do your scrapping logic  using driver.pagesource
            # print("States ==== " + str(page_url))
            soup_location = BeautifulSoup(driver.page_source, "lxml")
            hours_of_operation  = " ".join(list(soup_location.find("td",{"id":"Inside_MainColumn"}).find("table").stripped_strings))
            geo_url  = soup_location.find("iframe")["src"]
            # print("geourl === "+ str(geo_url))
            latitude = geo_url.split("marker=")[1].split("%2C")[0]
            longitude = geo_url.split("marker=")[1].split("%2C")[1]
            # print("latitude === "+ str(latitude))
            # print("longitude "+ str(longitude))
            store = [locator_domain, location_name, street_address, city,state,zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation.replace("Hours of Operation: TBD","<MISSING>"), page_url]

            if str(store[2]) not in addresses and country_code:
                addresses.append(str(store[2]))
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store

            driver.back()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
