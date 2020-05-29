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

def addy_extractor(src):
    arr = src.split(',')
    if len(arr) == 3:
        city = arr[0].strip()
        state = arr[1].strip()
        zip_code = arr[2].strip()
    else:
        city = arr[0]
        prov_zip = arr[1].strip().split(' ')
        state = prov_zip[0].strip()
        zip_code = prov_zip[1].strip()

    return city, state, zip_code

def fetch_data():
    # Your scraper here

    locator_domain = 'https://jitteryjoes.com/'
    ext = 'pages/cafes'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    divs = driver.find_elements_by_css_selector('div.info')
    all_store_data = []
    for div in divs:
        content = div.text.split('\n')
        if '15 Hikage' in content[2]:
            continue

        location_name = content[1]
        street_address = content[2]
        if 'RITZ-CARLTON' in location_name:
            addy = content[3].split(',')
            city = addy[0]
            state = addy[1].strip()
            zip_code = '<MISSING>'
        else:
            city, state, zip_code = addy_extractor(content[3])

        if len(content) > 4:
            if 'M-F:' in content[4]:
                hours = content[4]
                phone_number = '<MISSING>'
            else:
                phone_number = content[4].replace('ph.', '').strip()

            if len(content) == 7:
                hours = content[5] + ' ' + content[6]
            elif len(content) == 8:
                hours = content[5] + ' ' + content[6] + ' ' + content[7]
            elif len(content) == 10:
                hours = content[5] + ' ' + content[6] + ' ' + content[7] + ' ' + content[8]
        else:
            hours = '<MISSING>'

        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        print(store_data)
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
