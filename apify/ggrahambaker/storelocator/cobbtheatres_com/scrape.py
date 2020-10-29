import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.common.action_chains import ActionChains
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cobbtheatres_com')



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
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1].replace('.', '')
        zip_code = prov_zip[2]

    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://cobbtheatres.com/'
    ext = 'theatres.asp'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    a_tags = driver.find_elements_by_css_selector("a.drop")
    locs = a_tags[0]

    hover = ActionChains(driver).move_to_element(locs)
    hover.perform()

    theater_locs = driver.find_element_by_css_selector('div.col_1.firstcolumn').find_elements_by_css_selector('a')
    href_arr = []
    for thea in theater_locs:
        href = thea.get_attribute("href")
        name = thea.get_attribute('title')
        if name == '':
            idx = href.find('.com')
            name = href[idx + 5:]
            if '.' in name:
                name = name[:-5]
            else:
                name = name.split('/')[-1].replace('-', ' ')

        href_arr.append([href, name])

    all_store_data = []
    for href in href_arr:
        if 'https://www.cmxcinemas.com/' in  href[0]:
            continue
        cut = href[0].find('.com')
        locator_domain = href[0][:cut + 5]
        location_name = href[1]
        if 'cobb' in href[0]:
            driver.implicitly_wait(10)
            driver.get(href[0])

            content = driver.find_element_by_css_selector('div#tabcontent')
            lines = content.find_element_by_css_selector('p').text.split('\n')
            # normal case
            if len(lines) == 4:
                street_address = lines[0]
                if 'Cobb' in street_address:
                    city, state, zip_code = addy_extractor(lines[2])
                    phone_number = lines[3].replace('Movie Times: ', '')
                elif ',' in lines[1]:
                    city, state, zip_code = addy_extractor(lines[1])
                    phone_number = lines[3].replace('Movie Times: ', '')

                else:
                    street_address += ' ' + lines[1]
                    city, state, zip_code = addy_extractor(lines[2])
                    phone_number = lines[3].replace('Movie Times: ', '')
            elif len(lines) == 3:
                street_address = lines[0]
                city, state, zip_code = addy_extractor(lines[1])
                phone_number = lines[2].replace('Movie Times: ', '')
            else:
                if '1850 Legends Lane' in lines[0]:
                    street_address = lines[0] + ' ' + lines[1]
                    city, state, zip_code = addy_extractor(lines[2])
                    phone_number = lines[-1].replace('Movie Times: ', '')
                else:
                    street_address = lines[0]
                    city, state, zip_code = addy_extractor(lines[1])
                    phone_number = lines[2].replace('Movie Times: ', '')

        elif 'cinebistro' in href[0]:
            driver.implicitly_wait(10)
            driver.get(href[0])

            content = driver.find_element_by_css_selector('div.vcard')
            lines = content.text.split('\n')
            # logger.info(len(lines))
            # logger.info(lines)
            if len(lines) == 4:
                street_address = lines[0]
                city, state, zip_code = addy_extractor(lines[1])
                phone_number = lines[2]
            elif len(lines) == 5:
                street_address = lines[1]
                city, state, zip_code = addy_extractor(lines[2])
                phone_number = lines[3]
            elif len(lines) == 6:
                street_address = lines[1]
                city, state, zip_code = addy_extractor(lines[2])
                phone_number = lines[-2]
            elif len(lines) == 7:
                street_address = lines[1]
                city, state, zip_code = addy_extractor(lines[2])
                phone_number = lines[-2]
            else:
                street_address = lines[1]
                city, state, zip_code = addy_extractor(lines[2])
                phone_number = lines[3]

        elif 'cmx' in href[0]:
            driver.implicitly_wait(10)
            driver.get(href[0])
            content = driver.find_element_by_css_selector('div.cinema-info')
            ps = content.find_elements_by_css_selector('p')
            address = ps[0].text.replace('ADDRESS: ', '').split(',')
            street_address = address[0]
            city = address[1]
            state = address[2].strip().split(' ')[0]
            zip_code = address[2].strip().split(' ')[1]
            phone_number = ps[1].text.replace('PHONE: ', '')

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'

        all_store_data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code,
                               store_number, phone_number, location_type, lat, longit, hours])

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
