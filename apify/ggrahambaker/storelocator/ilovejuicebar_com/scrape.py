import csv
import os
from sgselenium import SgSelenium
import json
import re




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
    locator_domain = 'https://ilovejuicebar.com/'
    ext = 'locations-1'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    states = driver.find_elements_by_css_selector('section.Index-page')
    link_list = []
    for state in states:
        hrefs = state.find_elements_by_css_selector('a')
        for href in hrefs:
            if 'locations-1' not in href.get_attribute('href'):
                link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(30)
        main = driver.find_element_by_css_selector('section.Main-content').text.split('\n')
        location_name = main[0]

        if len(main) < 10:
            if '13317 shelbyville rd' in main[1] or '109 old camp rd.' in main[1] or '10283 clayton road' in main[
                1] or '9849 manchester road' in main[1]:
                street_address = main[1]
                city, state, zip_code = addy_ext(main[2])
            elif '222 11th ave. south' in main[1] or '2726 n mt. juliet rd.' in main[1] or '412 mclemore ave' in main[
                1] or '4801 kingston pike' in main[1]:
                street_address = main[1]
                city, state, zip_code = addy_ext(main[2])
            elif '11681 parkside drive' in main[1] or '950 w. stacy rd. suite 140' in main[
                1] or '4217 n. mccoll, suite 5' in main[1]:
                street_address = main[1]
                city, state, zip_code = addy_ext(main[2])
            elif '2701 cross timbers road, suite 238' in main[1]:
                street_address = main[1]
                city = 'flower mound'
                state = 'tx'
                zip_code = '75028'
            elif '62 morrill way' in main[1]:
                street_address = main[1]
                city, state, zip_code = addy_ext(main[2])
            elif '1350 concourse avenue' in main[1]:
                street_address = main[1]
                city = 'memphis'
                state = 'tennessee'
                zip_code = '38104'
            elif '301 n. custer rd. suite 100' in main[5]:
                street_address = main[5]
                city, state, zip_code = addy_ext(main[6])
            elif '2120 green hills village drive' in main[2]:
                street_address = main[2]
                city, state, zip_code = addy_ext(main[3])
            else:
                street_address = main[1] + ' ' + main[2]
                city, state, zip_code = addy_ext(main[3])
        else:
            if '1095 old peachtree road' in main[2] or '2521 airport thruway' in main[2] or '3115 crooks road' in main[2] or '7504 beechmont ave' in main[2] or '1120 4th avenue north #101' in main[2] or '10283 clayton road' in main[2] or '553 south cooper' in main[2]:
                street_address = main[2]
                city, state, zip_code = addy_ext(main[3])
            else:
                street_address = main[2] + ' ' + main[3]
                if 'suite 100 charlotte' in street_address:
                    street_address = main[1] + ' ' + main[2]
                    city = 'charlotte'
                    state = 'nc'
                    zip_code = '28204'
                elif '6425 wilkinson blvd' in street_address:
                    city = 'belmont'
                    state = 'nc'
                    zip_code = '28012'
                elif '7324 gaston ave, suite 123' in main[1]:
                    street_address = main[1]
                    city, state, zip_code = addy_ext(main[2])
                elif '1754 sc-160 w' in main[1]:
                    street_address = main[1] + ' ' + main[2]
                    city, state, zip_code = addy_ext(main[3])
                elif '804 north thompson lane' in main[1]:
                    street_address = main[1] + ' ' + main[2]
                    city, state, zip_code = addy_ext(main[3])
                elif '232 fifth avenue north' in main[2]:
                    street_address = main[2]
                    city, state, zip_code = addy_ext(main[3])
                elif '5040 carothers parkway' in main[3]:
                    street_address = main[3] + ' ' + main[4]
                    city, state, zip_code = addy_ext(main[5])
                elif '7407 igou gap road, suite 113' in main[1]:
                    street_address = main[1]
                    city, state, zip_code = addy_ext(main[2])
                elif '4021 preston rd, suite 616' in main[1]:
                    street_address = main[1]
                    city, state, zip_code = addy_ext(main[2])
                elif '8018 park lane, suite 120' in main[2]:
                    street_address = main[2]
                    city, state, zip_code = addy_ext(main[3])

                else:
                    city, state, zip_code = addy_ext(main[4])

        hours = ''
        phone_number = ''
        for h in main:
            if '//' in h:
                hours += h + ' '
            if re.search('([\-\+]{0,1}\d[\d\.\,]*[\.\,][\d\.\,]*\d+)', h):
                phone_number = re.search('([\-\+]{0,1}\d[\d\.\,]*[\.\,][\d\.\,]*\d+)', h).group()



        hours = hours.strip()

        if hours == '':
            hours = '<MISSING>'
        if phone_number == '':
            phone_number = '<MISSING>'
        data = driver.find_element_by_css_selector('div.sqs-block.map-block.sqs-block-map').get_attribute(
            'data-block-json')
        json_coord = json.loads(data)

        lat = json_coord['location']['markerLat']
        longit = json_coord['location']['markerLng']

        location_type = '<MISSING>'
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
