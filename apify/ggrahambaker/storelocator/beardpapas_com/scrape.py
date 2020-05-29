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
    locator_domain = 'https://beardpapas.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, '/location-categories/')]")
    link_list = []
    for href in hrefs:
        link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)

        h = driver.execute_script("return document.body.scrollHeight")
        driver.implicitly_wait(10)
        driver.execute_script("window.scrollTo(0, 0)")
        for i in range(0, h, 60):
            # load content
            driver.execute_script("window.scrollTo(0, " + str(i) + ")")
            time.sleep(.4)

        locs = driver.find_elements_by_css_selector('div.location-block')

        for loc in locs:
            content = loc.text.split('\n')

            location_name = content[0]
            if 'BC' in content[2]:
                # canada

                addy = content[2].split(' ')
                street_address = addy[0] + ' ' + addy[1] + ' ' + addy[2].replace(',', '')
                city = addy[3].replace(',', '')
                state = addy[4].replace(',', '')
                zip_code = addy[5] + ' ' + addy[6].replace(',', '')
                country_code = 'CA'

            else:
                if 'Suite 200 Unit 103' in content[2]:
                    street_address = '9292 Warren Parkway Suite 200 Unit 103'
                    city = 'Frisco'
                    state = 'TX'
                    zip_code = '75034'
                else:
                    parsed_add = usaddress.tag(content[2])[0]

                    street_address = ''

                    if 'AddressNumber' in parsed_add:
                        street_address += parsed_add['AddressNumber'] + ' '
                    if 'StreetNamePreDirectional' in parsed_add:
                        street_address += parsed_add['StreetNamePreDirectional'] + ' '
                    if 'StreetName' in parsed_add:
                        street_address += parsed_add['StreetName'] + ' '
                    if 'StreetNamePostType' in parsed_add:
                        street_address += parsed_add['StreetNamePostType'] + ' '
                    if 'OccupancyType' in parsed_add:
                        street_address += parsed_add['OccupancyType'] + ' '
                    if 'OccupancyIdentifier' in parsed_add:
                        street_address += parsed_add['OccupancyIdentifier'] + ' '
                    city = parsed_add['PlaceName']
                    state = parsed_add['StateName']
                    zip_code = parsed_add['ZipCode']
                country_code = 'US'

            phone_number = content[4]

            if '808-942-280' in phone_number:
                phone_number = '<MISSING>'

            hours = ''
            for h in content[6:-1]:
                hours += h + ' '

            lat = '<MISSING>'
            longit = '<MISSING>'

            location_type = '<MISSING>'
            store_number = '<MISSING>'

            hours = hours.strip()
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
