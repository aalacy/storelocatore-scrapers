import csv
import os
from sgselenium import SgSelenium
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    if len(address) == 3:
        city = address[0]
        state = address[1].strip()
        zip_code = address[2].strip()
    else:
        city = address[0]
        state_zip = address[1].strip().split(' ')

        state = state_zip[0].strip()
        zip_code = state_zip[1] + ' ' + state_zip[2]

    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.patene.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locs = driver.find_elements_by_xpath('//div[@class="location-details-container"]')
    all_store_data = []
    for loc in locs:
        soup = BeautifulSoup(loc.get_attribute('innerHTML'), 'html.parser')

        location_name = soup.find('strong').text

        info_ptags = soup.find_all('p')
        street_address = info_ptags[0].text
        city, state, zip_code = addy_ext(info_ptags[1].text)

        phone_number = info_ptags[2].text.replace('tel:', '').strip()

        coords_link = soup.find('a')['href']

        start_idx = coords_link.find('ll=')
        if start_idx > 0:
            ## do the rest
            if 'pickering' in coords_link:
                end_idx = coords_link.find('&sp')
            else:
                end_idx = coords_link.find('&ss')

            coords = coords_link[start_idx + 3: end_idx].split(',')
            lat = coords[0]
            longit = coords[1]

        else:
            start_idx = coords_link.find('/@')
            if start_idx > 0:
                ## do the rest
                end_idx = coords_link.find('/data')
                coords = coords_link[start_idx + 2: end_idx].split(',')
                lat = coords[0]
                longit = coords[1]
            else:
                lat = '<MISSING>'
                longit = '<MISSING>'

        country_code = 'CA'
        store_number = '<MISSING>'
        hours = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
