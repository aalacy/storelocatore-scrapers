import requests
from bs4 import BeautifulSoup
import csv
import usaddress
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    #return webdriver.Chrome('chromedriver', chrome_options=options)
    return webdriver.Chrome('/Users/Dell/local/chromedriver',chrome_options=options)

def fetch_data():
    # Your scraper here
    data = []
    p = 1
    driver = webdriver.Chrome('/Users/Dell/local/chromedriver')
    links = []
    prov = []
    url = "http://www.redapplestores.com/store/52974/"
    driver.get(url)
    time.sleep(5)
    container = driver.find_element_by_class_name("disallow")
    container.click()

    province_box = driver.find_element_by_id("province-selector")
    poption = province_box.find_elements_by_tag_name('option')
    for n in range(1,len(poption)):
        print(poption[n].get_attribute('value'))
        province = poption[n].get_attribute('value')
        prov.append(province)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    for i in range(0, len(prov)):
        s1 = Select(driver.find_element_by_id("province-selector"))
        s1.select_by_value(prov[i])
        print(prov[i])
        print("checking.....")
        city_box = driver.find_element_by_id("city-selector")
        time.sleep(10)
        coption = city_box.find_elements_by_tag_name('option')
        for j in range(1,len(coption)):
            city = coption[j].get_attribute("value")
            link = "http://www.redapplestores.com" + city
            print(link)
            links.append(link)

    driver.quit()
    for n in range(0,len(links)):
        driver = get_driver()
        driver.get(links[n])
        time.sleep(2)
        title = driver.find_element_by_id("store_title").text

        address = driver.find_element_by_id("store_address").text
        address = usaddress.parse(address)
        print(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                    temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1 or temp[1].find("LandmarkName") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        phone = driver.find_element_by_id("store_phone").text

        hours = str(driver.find_element_by_id("store_hours").text)
        hours = hours.replace("\n", " | ")
        street = street.lstrip()
        city = city.lstrip()
        state = state.lstrip()
        phone = phone.lstrip()
        pcode = pcode.lstrip()

        street = street.replace(",", "")
        street = street.replace("(", "")
        street = street.replace(")", "")
        city = city.replace(",", "")
        city = city.replace("(", "")
        city = city.replace(")", "")
        title = title.replace(",", "")

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

        print(title)
        print(street)
        print(city)
        print(state)
        print(pcode)
        print(phone)
        print(hours)
        print(p)
        print("......................................")
        data.append([
            url,
            title,
            street,
            city,
            state,
            pcode,
            "CA",
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
