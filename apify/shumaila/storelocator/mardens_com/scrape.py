import requests
from bs4 import BeautifulSoup
import csv
import usaddress
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)
    #return webdriver.Chrome('/Users/Dell/local/chromedriver', chrome_options=options)

def fetch_data():
    # Your scraper here
    data = []
    p = 1
    driver = get_driver()
    data = []
    url = "https://www.mardens.com/"
    driver.get(url)
    time.sleep(2)

    details = driver.find_elements_by_class_name("location-block")
    print(len(details))
    p = 1
    for n in range(0, len(details)):
        print(details[n].get_attribute('href'))
        link = details[n].get_attribute('href')
        driver = get_driver()
        driver.get(link)
        time.sleep(1)
        title = driver.find_element_by_tag_name('h1').text
        hours = driver.find_element_by_class_name("hours").text
        hours = hours.replace("HOURS:\n","")
        hours = hours.replace("\n", "|")
        address = driver.find_element_by_class_name("location-address").text
        address = usaddress.parse(address)
        print(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        ccode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                    temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1 or temp[1].find("LandmarkName") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            if temp[1].find("CountryName") != -1:
                ccode = "US"
            i += 1
        phone = driver.find_element_by_class_name("location-phone").text
        if len(ccode) < 2 and state.find("USA") > -1:
            ccode = "US"
            state = state[0:state.find("USA")-1]
            pcode = "<MISSING>"
        street = street.lstrip()
        city = city.lstrip()
        state = state.lstrip()
        phone = phone.lstrip()
        pcode = pcode.lstrip()
        ccode = ccode.lstrip()
        street = street.replace(",", "")
        city = city.replace(",", "")
        state = state.replace(",", "")
        pcode = pcode.replace(",", "")
        print(p)
        print(title)
        print(street)
        print(city)
        print(state)
        print(pcode)
        print(ccode)
        print(phone)
        print(hours)

        data.append([
            url,
            title,
            street,
            city,
            state,
            pcode,
            "US",
            "<MISSING>",
            phone,
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
            hours
        ])
        p += 1

    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
