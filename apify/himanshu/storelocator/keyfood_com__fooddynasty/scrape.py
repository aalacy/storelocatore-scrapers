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
    base_url = "https://www.keyfood.com/#fooddynasty"

    addresses = []
    driver = get_driver()
    driver.get("http://keyfood.mywebgrocer.com/StoreLocator.aspx")
    states = []

    # driver.find_element_by_xpath("//select[@name='selStates']").click()
    for button in driver.find_elements_by_xpath("//select[@name='selStates']/option"):
        state = button.get_attribute("value")
        if len(state) != 2:
            continue
        states.append(state)

    for state in states:
        driver.find_element_by_xpath("//select[@name='selStates']").click()
        driver.find_element_by_xpath("//option[@value='" + state + "']").click()
        WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath("//option[@value='']"))  # wait until data
        driver.find_element_by_xpath("//input[@class='submitButton']").click()

        # print("States ==== " + str(state))
        soup = BeautifulSoup(driver.page_source,"lxml")

        for location_script in soup.find_all("div",{"class":"StoreBox"}):

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

            geo_url = location_script.find("a")["href"]
            # print("geo_url === "+ geo_url)
            if geo_url.count("ll="):
                latitude = str(geo_url.split("ll=")[1].split(",")[0])
                longitude = str(geo_url.split("ll=")[1].split(",")[1])

            location_name = location_script.find("p",{"class":"StoreTitle"}).text
            street_address = location_script.find_all("p",{"class":"tInfo"})[0].text
            city_state_zipp = location_script.find_all("p",{"class":"tInfo"})[1].text

            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(city_state_zipp))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(city_state_zipp))
            state_list = re.findall(r' ([A-Z]{2}) ', str(city_state_zipp))

            if ca_zip_list:
                zipp = ca_zip_list[0]
                country_code = "CA"

            if us_zip_list:
                zipp = us_zip_list[0]
                country_code = "US"

            if state_list:
                state = state_list[0]

            city = city_state_zipp.replace(zipp, "").replace(state, "").replace(",", "")

            hours_of_operation = " ".join(list(location_script.find("div",{"class":"StoreHours"}).stripped_strings))
            phone_data = " ".join(list(location_script.find("div",{"class":"StoreContact"}).stripped_strings))

            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_data))
            if phone_list:
                phone = phone_list[-1]

            # print("phone === "+ phone)
            # print("city_state_zipp === "+ city_state_zipp)

            # do your logic here.

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[1]) + str(store[2]) not in addresses:
                addresses.append(str(store[1]) + str(store[2]))

                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
