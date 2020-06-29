import csv
import os
from sgselenium import SgSelenium
import json
from bs4 import BeautifulSoup


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://trufitathleticclubs.com/'
    ext = 'texas/locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    base = BeautifulSoup(driver.page_source,"lxml")
    all_scripts = base.find_all("script")
    for script in all_scripts:
        script_str = str(script)
        if "latitude" in script_str:
            break

    final_script = script_str[script_str.find("stores:")+8:script_str.rfind("]},")+2]
    data_json = json.loads(final_script)

    all_store_data = []
    found_gps = []
    for location in data_json:
        raw_data = data_json[location]
        for data in raw_data:

            location_name = data["ClubName"]
            street_address = data["Address1"]
            city = data["City"]
            state = data["State"]
            zip_code = data["ZipCode"]
            phone_number = data["phone"]

            hours = data["LocationHours"].replace("{","").replace('"',"").replace("}","")

            country_code = 'US'
            store_number = data["ClubId"]
            location_type = '<MISSING>'
            lat = data["latitude"]
            longit = data["longitude"]

            if street_address == "5330 WALZEM":
                lat = "29.5085296"
                longit = "-98.389204"

            if street_address == "3205 N CONWAY AVE":
                lat = "26.2452395"
                longit = "-98.3239731"

            lat_long = lat + "_" + longit
            if lat_long in found_gps:
                lat = '<MISSING>'
                longit = '<MISSING>'
            else:
                found_gps.append(lat_long)


            page_url = locator_domain + ext
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours, page_url]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
