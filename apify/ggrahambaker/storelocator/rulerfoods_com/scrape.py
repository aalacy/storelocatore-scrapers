import csv
import os
from sgselenium import SgSelenium
import usaddress
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://rulerfoods.com/'
    ext = 'locations/'
    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    obj = driver.switch_to.alert
    obj.accept()

    element = driver.find_element_by_css_selector('span.popup-close')
    driver.execute_script("arguments[0].click();", element)

    all_store_data = []
    # ten pages

    inputElement = driver.find_element_by_id("addressInput")
    inputElement.send_keys('kentuky')
    inputElement.submit()
    time.sleep(2)
    for i in range(1, 11):
        main = driver.find_element_by_css_selector('div#map_sidebar')

        lis = main.find_elements_by_css_selector('div.results_wrapper.cf')
        for li in lis:
            content = li.find_element_by_css_selector('div.results_entry.location_primary').text.split('\n')
            if len(content) > 1:
                phone_hours = content[1].split('PM')#.strip()
                hours = phone_hours[0] + ' PM'
                phone_number = phone_hours[1]
                parsed_add = usaddress.tag(content[0])[0]

                street_address = ''
                street_address += parsed_add['AddressNumber'] + ' '
                if 'StreetNamePreDirectional' in parsed_add:
                    street_address += parsed_add['StreetNamePreDirectional'] + ' '

                street_address += parsed_add['StreetName'] + ' '
                if 'StreetNamePostType' in parsed_add:
                    street_address += parsed_add['StreetNamePostType'] + ' '
                if 'OccupancyType' in parsed_add:
                    street_address += parsed_add['OccupancyType'] + ' '
                if 'OccupancyIdentifier' in parsed_add:
                    street_address += parsed_add['OccupancyIdentifier'] + ' '

                street_address = street_address.strip()
                city = parsed_add['PlaceName']
                state = parsed_add['StateName']
                zip_code = parsed_add['ZipCode']
                if '1129 N. BALDWIN AVE.' in street_address:
                    zip_code = '46952'

                country_code = 'US'
                location_type = '<MISSING>'
                store_number = '<MISSING>'
                lat = '<MISSING>'
                longit = '<MISSING>'
                location_name = '<MISSING>'

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

        time.sleep(2)

        element = driver.find_element_by_css_selector('a.next_link')

        driver.execute_script("arguments[0].click();", element)

    driver.quit()

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
