import csv
import os
from sgselenium import SgSelenium
import time
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def clean_loc(arr):
    to_ret = []
    for element in arr:
        if 'VIEW MENU' in element:
            continue
        elif 'ORDER ONLINE' in element:
            continue
        elif 'CATERING MENU' in element:
            continue
        elif 'Delivery Charge:' in element:
            continue
        elif 'Beer Wine Now Served' in element:
            continue
        elif 'Dine-in Now Available' in element:
            continue
        elif 'Hours may vary by season' in element:
            continue
        elif '_______________________' in element:
            continue
        elif 'Ask us about pre-ordering outside of ' in element:
            continue
        elif '(see store window posting)' in element:
            continue
        elif 'North of the BMW Dealership and in front of the Jamaica Bay Community' in element:
            continue
        elif 'Please note that last call for all delivery/carryout orders is 15 mins prior to closing.' in element:
            continue
        elif 'WITH GRUBHUB' in element:
            continue
        else:
            to_ret.append(element)

    return to_ret

def fetch_data():
    locator_domain = 'https://myrosatis.com/'
    ext = 'locations/all-locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.get(locator_domain + ext)
    states = driver.find_elements_by_css_selector('div.accordion-group')
    link_list = []
    for state in states:
        i = state.find_element_by_css_selector('div.accordion-head')
        driver.execute_script("arguments[0].click();", i)
        time.sleep(1)
        lis = state.find_elements_by_css_selector('li')
        for li in lis:
            if 'COMING SOON' in li.text:
                continue
            if 'TEMPORARILY CLOSED' in li.text:
                continue

            link_list.append(li.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        t = driver.find_element_by_css_selector('div.section-body-location').text.split('\n')
        content = clean_loc(t)

        location_name = content[0]
        if 'SCOTTSDALE PIMA' in location_name:
            location_name += content[1]
            content = content[1:]
        location_type = content[1].replace('[', '').replace(']', '').replace('   ', ' ').strip()
        phone_number = content[2].replace('Phone:', '').strip()
        addy = content[3].replace('(map it)', '').strip()
        parsed_add = usaddress.tag(addy)[0]
        # print(parsed_add)
        street_address = ''
        if 'AddressNumber' in parsed_add:
            street_address += parsed_add['AddressNumber'] + ' '
        if 'StreetNamePreDirectional' in parsed_add:
            street_address += parsed_add['StreetNamePreDirectional'] + ' '
        if 'StreetName' in parsed_add:
            street_address += parsed_add['StreetName'] + ' '
        if 'StreetNamePostType' in parsed_add:
            street_address += parsed_add['StreetNamePostType']
        if 'StreetNamePostDirectional' in parsed_add:
            street_address += parsed_add['StreetNamePostDirectional']
        if 'OccupancyType' in parsed_add:
            street_address += parsed_add['OccupancyType']
        if 'OccupancyIdentifier' in parsed_add:
            street_address += parsed_add['OccupancyIdentifier']

        city = parsed_add['PlaceName']
        state = parsed_add['StateName']
        zip_code = parsed_add['ZipCode']
        if 'AZ' in state:
            if '89086' in zip_code:
                zip_code = '<MISSING>'
            if '83524' in zip_code:
                zip_code = '<MISSING>'
        if 'IN' in state:
            if '46300' in zip_code:
                zip_code = '<MISSING>'

        hours = ''
        for h in content[4:]:
            hours += h + ' '

        hours = hours.strip()
        href = driver.find_element_by_css_selector('span.location').find_element_by_css_selector('a').get_attribute(
            'href')
        start_idx = href.find('c:')
        if start_idx > 0:
            coords = href[start_idx + 2:].split(',')
            lat = coords[0]
            longit = coords[1]
        else:
            lat = '<MISSING>'
            longit = '<MISSING>'

        store_number = '<MISSING>'
        country_code = 'US'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
