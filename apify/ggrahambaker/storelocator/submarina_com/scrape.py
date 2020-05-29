import csv
import os
from sgselenium import SgSelenium




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def addy_ext(addy):
    address = addy.split(' ')
    if len(address) == 4:
        city = address[0] + ' ' + address[1]
        state = address[2]
        zip_code = address[3]
    else:
        city = address[0]
        state = address[1]
        zip_code = address[2]
    return city, state, zip_code


def fetch_data():
    locator_domain = 'http://submarina.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    all_store_data = []
    divs = driver.find_elements_by_css_selector('div.fusion-text')
    for div in divs:
        cont = div.text.split('\n')
        if len(cont) < 5:
            continue

        location_name = cont[0]

        street_address = cont[1]
        city, state, zip_code = addy_ext(cont[2])

        phone_number = cont[3]
        hours = ''
        for h in cont[4:]:
            hours += h + ' '

        hours = hours.strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
