import csv
import os
import time
from selenium.webdriver.support.wait import WebDriverWait
from sgselenium import SgSelenium
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'http://www.freshieslobsterco.com/'
    ext = 'locations'
    driver = SgSelenium().firefox()
    driver.get(locator_domain + ext)
    ids = ['#block-yui_3_17_2_1_1534822643996_26234', '#block-yui_3_17_2_1_1534822643996_5344']
    all_store_data = []
    for id_tag in ids:
        content = driver.find_element_by_css_selector('div' + id_tag).text.split('\n')
        location_name = content[0].strip()
        parsed_add = usaddress.tag(content[1])[0]
        street_address = ''
        street_address += parsed_add['AddressNumber'] + ' '
        if 'StreetNamePreDirectional' in parsed_add:
            street_address += parsed_add['StreetNamePreDirectional'] + ' '
        street_address += parsed_add['StreetName'] + ' '
        if 'StreetNamePostType' in parsed_add:
            street_address += parsed_add['StreetNamePostType']
        if 'StreetNamePostDirectional' in parsed_add:
            street_address += parsed_add['StreetNamePostDirectional']
        city = parsed_add['PlaceName']
        state = parsed_add['StateName']
        zip_code = parsed_add['ZipCode']
        hours = content[2] + ' ' + content[3]
        if "84111" in zip_code:
            try:
                phone_number = hours.split("11-8")[1]
                hours =  hours.split(" 801")[0]
            except:
                phone_number = '<MISSING>'
                hours = '<MISSING>'
        else:
            phone_number = "435.631.9861"
        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url= "http://www.freshieslobsterco.com/locations"
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours,page_url]
        all_store_data.append(store_data)
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
