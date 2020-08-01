import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
import time
from selenium.webdriver.support.wait import WebDriverWait





def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    driver = SgSelenium().firefox()
    return_main_object = []
    addresses = []

    locator_domain = "https://www.bahamabucks.com/"
    page_url = "<MISSING>"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = 'https://www.bahamabucks.com/locations/index.html'

    driver.get("https://www.bahamabucks.com/sc/fns/locations.php")
    s = requests.Session()
    cookies_list = driver.get_cookies()

    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie['name']] = cookie['value']

    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(
        ",", ";")

    # print(cookies_string)

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Cookie": cookies_string


    }
    add = []
    hours = []
    page_url1 = []
    data = "status=All"
    r = s.post(
        "https://www.bahamabucks.com/sc/fns/locations.php", data=data, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for info in soup.find("div", {"class": "container"}).find_all("div", class_="row"):
        list_info = list(info.stripped_strings)
        location_name = list_info[0].strip()
        street_address = list_info[1].strip()
        city = list_info[2].split(',')[0].strip()
        state = list_info[2].split(',')[-1].split()[0].strip()
        zipp = list_info[2].split(',')[-1].split()[-1].strip()
        phone = list_info[3].strip()
        hours_of_operation = " ".join(list_info[5:]).strip()
        latitude = info.find(
            'img', {"alt": "Get Directions"}).parent["href"].split("'")[-2].split(',')[0].strip()
        longitude = info.find(
            'img', {"alt": "Get Directions"}).parent["href"].split("'")[-2].split(',')[-1].replace("'", "").strip()
        if "HOURS" == phone:
            phone = "<MISSING>"
            hours_of_operation = " ".join(list_info[4:]).strip()
            # print(phone, hours_of_operation)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = ["<MISSING>" if x == "" or x == None else x for x in store]
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]

        if street_address in addresses:
            continue
        addresses.append(street_address)
        # print(state)
        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
