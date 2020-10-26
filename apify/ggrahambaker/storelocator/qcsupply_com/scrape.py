import csv
import os

from sgselenium import SgSelenium
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re
import time
from bs4 import BeautifulSoup
from random import randint


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = 'https://www.qcsupply.com/locations/'
    locator_domain = 'qcsupply.com'

    driver = SgSelenium().chrome()
    time.sleep(2)

    driver.get(base_link)
    time.sleep(randint(2,4))

    element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.NAME, "leftLocation")))

    all_store_data = []
    all_links = []

    spans = driver.find_elements_by_name('leftLocation')

    print("Getting all POI links ..")
    for span in spans:
        raw_link = span.find_element_by_class_name("location_link").find_element_by_tag_name("span").get_attribute("onclick")
        link = "https://www.qcsupply.com/" + raw_link.split("='/")[-1].replace("'","")
        store_number = span.get_attribute('data-amid')
        all_links.append([link, store_number])
    print("Done!")

    total_links = len(all_links)
    for i, raw_link in enumerate(all_links):
        print("Link %s of %s" %(i+1,total_links))
        link = raw_link[0]
        store_number = raw_link[1]

        print(link)
        driver.get(link)
        time.sleep(randint(2,4))

        try:
            element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
                (By.CLASS_NAME, "map")))
            time.sleep(randint(3,5))
            raw_gps = driver.find_element_by_xpath("//*[(@title='Open this area in Google Maps (opens a new window)')]").get_attribute("href")
            latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
            longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
        except:
            print('Timeout...')
            latitude = '<INACCESSIBLE>'
            longitude = '<INACCESSIBLE>'

        item = BeautifulSoup(driver.page_source,"lxml")

        location_name = "QC Supply " + item.find("h2").text.strip()
        print(location_name)

        street_address = item.find(class_="address-line").text.strip()
        city_line = item.find_all(class_="address-line")[1].text.replace(u'\xa0', u'').strip()
        city = city_line[:city_line.find(",")]
        state = city_line[city_line.find(",")+1:city_line.rfind(" ")].strip()
        zip_code = city_line[city_line.rfind(" ")+1:].strip()
        phone_number = item.find_all(class_="address-line")[2].a.text.replace(u'\xa0', u'').strip()
        
        if '/' in phone_number:
            phone_number = phone_number.split('/')[0].strip()

        country_code = 'US'
        location_type = '<MISSING>'

        raw_hours = item.find_all(class_="location-address-inner")[2].text.replace(u'\xa0', u'').strip()
        hours = raw_hours.replace("\n"," ").replace("PM","PM ").strip()
        hours_of_operation = (re.sub(' +', ' ', hours)).strip()

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        
        store_data = [locator_domain, link, location_name, street_address, city, state, zip_code, country_code,
                         store_number, phone_number, location_type, latitude, longitude, hours_of_operation]
        all_store_data.append(store_data)

    # End scraper

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
