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
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    if len(prov_zip) == 1:
        zip_code = '<MISSING>'
    else:
        zip_code = prov_zip[1].strip()

    return city, state, zip_code




def fetch_data():
    locator_domain = 'https://theperfectpita.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    divs = driver.find_elements_by_css_selector('div.et_pb_text_inner')
    all_store_data = []
    for location in divs:
        content = location.text.split('\n')
        if len(content) > 1:
            location_name = content[0]
            street_address = content[2]
            if '2200 Clarendon Blvd' in street_address:
                city = 'Arlington'
                state = 'VA'
                zip_code = '<MISSING>'
            else:
                addy = content[3].replace('Underground', '').replace('behind Target', '').replace(
                    ' same building as Lasik', '').strip()
                city, state, zip_code = addy_extractor(addy)
            phone_number = content[4]
            if 'seasonal' in phone_number:
                phone_number = content[5]
                hours = content[6] + ' ' + content[7]
            elif 'Off King Street' in phone_number:
                phone_number = content[5]
                hours = content[6]
            else:
                hours = content[5]

            country_code = 'US'
            location_type = '<MISSING>'

            href = location.find_element_by_css_selector('a').get_attribute('href')
            start_idx = href.find('ll=')
            end_idx = href.find('&sspn')
            if start_idx == -1:
                lat = '<INACCESSIBLE>'
                longit = '<INACCESSIBLE>'
            else:
                coords = href[start_idx + 3:end_idx].split(',')

                lat = coords[0]
                longit = coords[1]
            store_number = '<MISSING>'

            phone_number = phone_number.replace('PITA', '7482')[:12]
            if 'or' in phone_number:
                phone_number = phone_number.split('or')[0]

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
