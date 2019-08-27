import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress
import re

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.malinandgoetz.com/'
    ext = 'storelocator/'
    driver = get_driver()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(60)



    pop = driver.find_elements_by_xpath('//img[@data-popup-image-type="square_new"]')


    if len(pop) == 1:
        pop = driver.find_element_by_xpath('//img[@data-popup-image-type="square_new"]')
        driver.execute_script("arguments[0].click();", pop)



    lat_long_info = []
    driver.execute_script('MapManager.prototype.updateCountLabel = (() => console.log("update count label"))')
    try:
        driver.execute_script('window.onload()')
    except:
        print("failed")

    man = driver.execute_script('return mapManager.markers.reduce((accumulator, marker) => ({ ...accumulator, [marker.storelocator_id]: [marker.position.lat(), marker.position.lng(), marker.country, marker.element.innerText] }),{})')

    for store in man:
        if '(MALIN+GOETZ)' in man[store][3] and man[store][2] == 'US':
            street_address = man[store][3].split('\n\n')[1].split(',')[0]
            lat = man[store][0]
            longit = man[store][1]
            lat_long_info.append([street_address, lat, longit])


    ext2 = 'm-g-apothecaries'
    driver.get(locator_domain + ext2)
    driver.implicitly_wait(60)

    main = driver.find_element_by_css_selector('section#Content')
    ul = main.find_element_by_css_selector('ul')
    stores = ul.find_elements_by_css_selector('li')
    all_store_data = []
    for store in stores:
        content = store.text.split('\n')
        if 'London N1 1QY' in content[0]:
            break


        addy = content[0].replace('MALIN+GOETZ', '').strip()
        m = re.search("\d", addy)
        if m:
            location_name = addy[:m.start()]

        if 'Upper West Side' in addy:
            addy = addy.replace('Upper West Side', '').strip()
        if 'Upper East Side' in addy:
            addy = addy.replace('Upper East Side', '').strip()

        parsed_add = usaddress.tag(addy)[0]
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


        for lat_long in lat_long_info:
            if parsed_add['StreetName'] in lat_long[0]:
                lat =  lat_long[1]
                longit = lat_long[2]

        phone_number = content[2].replace('Tel:', '').strip()

        hours = ''
        for h in content[4:]:
            hours += h + ' '

        hours = hours.strip()

        country_code = 'US'

        store_number = '<MISSING>'
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
