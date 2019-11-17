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
    options.add_argument("--disable-notifications")
    return webdriver.Chrome('chromedriver', chrome_options=options)
    #return webdriver.Chrome('/Users/Dell/local/chromedriver', chrome_options=options)


def fetch_data():
    # Your scraper here
    data = []
    p = 1
    url = "http://highsstores.com/StoreLocator"
    driver1 = get_driver()
    driver1.get(url)
    time.sleep(10)
    #divs = driver.find_element_id("searchResultListing")
    stores = driver1.find_elements_by_class_name("div-srl-store-name")

    for n in range(0,len(stores)):
        store = stores[n].text
        start = store.find("#")
        store = store[start+1:len(store)]
        print(store)
        link = "http://highsstores.com/StoreHome/" + store
        print(link)
        driver = get_driver()
        driver.get(link)
        time.sleep(1)
        title = driver.find_element_by_xpath("/html/body/form/div[5]/div[3]/div[1]/div[1]/div/div[1]/div/h1").text
        street = driver.find_element_by_class_name("store-street-address").text
        city = driver.find_element_by_class_name("store-address-city").text
        state = driver.find_element_by_class_name("store-address-state").text
        pcode = driver.find_element_by_class_name("store-address-zip").text
        try:
            phone = driver.find_element_by_class_name("store-address-phone-number").text
        except:
            phone = "<MISSING>"
        hours = ""
        try:
            hours = driver.find_element_by_class_name("store-hours-open-24-7-span").text
        except:
            hours = driver.find_element_by_class_name("store-hours-container-div").text

        hours = hours.replace("\n", " ")

        detail = driver.find_element_by_xpath("/html/body/form/div[5]/div[3]/div[1]/div[2]/div/div[1]/div[1]/div[2]/div/div[1]")
        dnext= detail.find_element_by_tag_name("input").get_attribute("value")
        start = dnext.find("Longitude")
        start = dnext.find(":", start) + 1
        end = dnext.find(",", start)
        longt = dnext[start:end]
        start = dnext.find("Latitude")
        start = dnext.find(":", start) + 1
        end = dnext.find(",", start)
        lat = dnext[start:end]
        if len(street) < 4:
            address = "<MISSING>"
        if len(title) < 3:
            title = "<MISSING>"
        if len(city) < 3:
            city = "<MISSING>"
        if len(state) < 2:
            state = "<MISSING>"
        if len(pcode) < 5:
            pcode = "<MISSING>"
        if len(phone) < 5:
            phone = "<MISSING>"
        if len(hours) < 3:
            hours = "<MISSING>"
        if len(lat) < 3:
            lat = "<MISSING>"
        if len(longt) < 3:
            longt = "<MISSING>"

        print(title)
        print(street)
        print(city)
        print(state)
        print(pcode)
        print(phone)
        print(lat)
        print(longt)
        print(hours)

        print(p)
        print("......................................")
        p += 1

        data.append([
            url,
            title,
            street,
            city,
            state,
            pcode,
            "US",
            store,
            phone,
            "<MISSING>",
            lat,
            longt,
            hours
        ])
        driver.quit()

    driver1.quit()

    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
