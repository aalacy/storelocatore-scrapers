import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options



session = SgRequests()

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Firefox(options=options,executable_path="./geckodriver")


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    driver = get_driver()

    # print("soup ===  first")
    addresses = []
    base_url = "https://www.applebees.com"
    driver.get('https://www.applebees.com/en/restaurants?searchQuery=11576')

    cookies_list = driver.get_cookies()
    # print("cookies_list === " + str(cookies_list))
    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie['name']] = cookie['value']

    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(
        ",", ";")  # use for header cookie
    soup = BeautifulSoup(driver.page_source, "lxml")
    requestVerificationToken = soup.find("input", {"name": "__RequestVerificationToken"})["value"]  # use for body

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'cookie': cookies_string,
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    # print("cookies_string === "+ cookies_string)
    # print("requestVerificationToken === "+ requestVerificationToken)

    r_json = session.post("https://www.applebees.com/api/sitecore/Locations/LocationSearchAsync",
                           headers=headers,
                           data='ResultsPage=%2Flocations%2Fresults&LocationRoot=%7B3B216C7F-CB81-4126-A2CE-33AD79B379CF'
                                '%7D&NumberOfResults=10000&LoadResultsForCareers=False&MaxDistance=5000&UserLatitude'
                                '=&UserLongitude=&SearchQuery=11576&__RequestVerificationToken=' + str(
                               requestVerificationToken))
    json_data = r_json.json()

    # print("soup_json ==== "+ str(r_json.text))

    return_main_object = []

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = "presidentebarandgrill"
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""

    # print("soup  ==== " + str(soup))

    for location in json_data["Locations"]:

        # print("location ==== " + str(location))
        location_name = location["Location"]["Name"]
        store_number = location["Location"]["StoreNumber"]
        street_address = location["Location"]["Street"]
        city = location["Location"]["City"]
        state = location["Location"]["State"]
        country_code = location["Location"]["Country"]
        zipp = location["Location"]["Zip"]
        if location["Contact"] is not None:
            phone = location["Contact"]["Phone"]
        else:
            phone = ""
        latitude = location["Location"]["Coordinates"]["Latitude"]
        longitude = location["Location"]["Coordinates"]["Longitude"]

        hours_arr = location["HoursOfOperation"]["DaysOfOperationVM"]

        hours_of_operation = ""
        for days_hours in hours_arr:
            if days_hours["LocationHourText"] == " - ":
                hours_of_operation += days_hours["LocationHourLabel"] + " Close  "
            else:
                hours_of_operation += days_hours["LocationHourLabel"] + " " + days_hours["LocationHourText"] + "  "

        # print("store_number == " + str(country_code))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        if country_code == "US" or country_code == "CA":
            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

                store = [x if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
