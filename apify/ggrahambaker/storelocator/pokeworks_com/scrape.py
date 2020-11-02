import csv
import os
from sgselenium import SgSelenium
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def cleaner(addy):
    to_ret = []
    for a in addy:
        if a == '':
            continue
        elif a == ' ':
            continue
        elif 'CATERING' in a:
            continue
        elif 'Email catering' in a:
            continue
        elif 'Email Catering' in a:
            continue
        elif '@' in a:
            continue
        elif 'CATERING' in a:
            continue
        elif 'CATERING' in a:
            continue
        to_ret.append(' '.join(a.split()))

    return to_ret

def addy_ext(addy):
    country_code = 'US'
    address = addy.split(',')
    if len(address) == 3:
        city = address[0]
        state = address[1].strip()
        zip_code = address[2].strip()
    else:
        city = address[0]
        state_zip = address[1].strip().split(' ')
        if len(state_zip) == 4:
            state = state_zip[0]
            zip_code = state_zip[1] + ' ' + state_zip[2]
            country_code = 'CA'
        else:
            state = state_zip[0]
            zip_code = state_zip[1]
    return city, state, zip_code, country_code

def fetch_data():
    locator_domain = 'https://www.pokeworks.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)
    id_tags = ['block-yui_3_17_2_4_1518209608912_11294', 'block-yui_3_17_2_2_1518468705387_45075',
               'block-yui_3_17_2_8_1504639122263_32449']
    link_list = []
    for id_tag in id_tags:
        col = driver.find_element_by_css_selector('div#' + id_tag)
        a_tags = col.find_elements_by_css_selector('a')
        for a in a_tags:
            if a.get_attribute('href') == None:
                continue

            link_list.append(a.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)

        driver.implicitly_wait(10)
        map_json_string = driver.find_element_by_css_selector('div.sqs-block.map-block.sqs-block-map').get_attribute(
            'data-block-json')
        map_json = json.loads(map_json_string)['location']
        lat = map_json['markerLat']
        longit = map_json['markerLng']
        if 'philadelphia' in link:
            content = driver.find_elements_by_css_selector('div.sqs-block-content')[2].text.split('\n')
        else:
            content = driver.find_elements_by_css_selector('div.sqs-block-content')[3].text.split('\n')

        if len(content) > 1:
            content = cleaner(content)

            street_address = content[1].strip()

            if '1021 West Hastings' in street_address:
                city = 'Vancouver'
                state = 'B.C.'
                zip_code = 'V6E 2E9'
                phone_number = '(604) 332-8898'
                hours = 'Mon - Fri 11:00 am - 7:30 pm Sat - Sun 11:30 am - 6:30 pm'
                country_code = 'CA'
            elif 'Bellevue' in street_address:
                city, state, zip_code, country_code = addy_ext('Bellevue, WA 98004')
                phone_number = '(425) 214-1182'
                hours = content[4]
            elif '79 E Madison St' in street_address:
                city, state, zip_code, country_code = addy_ext(content[2].strip())
                phone_number = content[3]
                hours = content[4]
            else:
                city, state, zip_code, country_code = addy_ext(content[2].strip())
                phone_number = content[3].replace('TEL:', '').strip()

                hours = ''
                for h in content[5:]:
                    hours += h + ' '

                hours = hours.strip()

            store_number = '<MISSING>'
            location_type = '<MISSING>'
            location_name = link[link.find('com/') + 4:].replace('-', ' ').replace('1', '')
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
