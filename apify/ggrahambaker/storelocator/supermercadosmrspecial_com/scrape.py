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
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://supermercadosmrspecial.com/'
    ext = 'serviciosalcliente/supermercadoinfo.asp'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('ul.list_sup')
    stores = main.find_elements_by_css_selector('li')
    all_store_data = []
    for store in stores:
        container = store.find_element_by_css_selector('div')
        sections = container.find_elements_by_css_selector('div')

        location_name = sections[0].text
        if len(sections) == 4:
            hours = '<MISSING>'
            location_type = 'OFICINA CENTRAL'
            off = -1

        else:
            hours = sections[1].text.replace('Horario:', '').strip()
            location_type = 'TIENDA'
            off = 0

        addy = sections[off + 2].text.replace('Dirección:', '').strip().split('\n')
        if len(addy) == 2:
            street_address = addy[0]
            city, state, zip_code = addy_ext(addy[1])
        elif 'PR-2 Km 159,' in addy[0]:
            street_address = addy[0]
            city, state, zip_code = addy_ext(addy[1])
        else:
            addy = addy[0].split('Email')[0].split('.')
            street_address = addy[0]
            city, state, zip_code = addy_ext(addy[1].strip())

        phone_number = sections[off + 3].text.replace('Teléfonos:', '').strip()
        if '/' in phone_number:
            phone_number = phone_number.split('/')[0]
        google_href = sections[off + 4].find_element_by_css_selector('a').get_attribute('href')

        start_idx = google_href.find('?q=')
        end_idx = google_href.find('&key')
        coords = google_href[start_idx + 3:end_idx].split('%2C')
        lat = coords[0]
        longit = coords[1]

        country_code = 'US'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
