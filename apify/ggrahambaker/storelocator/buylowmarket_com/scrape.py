import csv
import os
from sgselenium import SgSelenium
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('buylowmarket_com')



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
    if len(arr) == 1:
        arr = src.split(' ')
        state = arr[0]
        zip_code = arr[1]
        city = '<MISSING>'
    else:
        city = arr[0]
        prov_zip = arr[1].split(' ')
        if len(prov_zip) == 3:
            state = prov_zip[1].replace('.', '')
            zip_code = prov_zip[2]

    return city, state, zip_code

def get_info(driver, tag, locator_domain, all_store_data):
    div = driver.find_element_by_css_selector('div' + tag)
    rows = div.find_elements_by_css_selector('div.row')
    logger.info(len(rows))
    for row in rows:
        stores = row.find_elements_by_css_selector('div.col-md-4')
        for store in stores:
            ps = store.find_elements_by_css_selector('p')
            if len(ps) == 0:
                continue
            else:
                location_name = ps[0].text
                # logger.info(location_name)
                ## all distro is the same, we only need one

                if '#' in location_name:
                    split = location_name.split('#')
                    if len(split) == 2:
                        store_number = split[1][:-1].strip()
                    elif len(split) == 3:
                        store_number = location_name.split('#')[1][:2].strip()
                else:
                    store_number = '<MISSING>'
                # logger.info(store_number)
                p_split = ps[1].text.split('\n')
                street_address = p_split[0]

                city, state, zip_code = addy_extractor(p_split[1])
                # logger.info(street_address)
                # logger.info(city, state, zip_code)
                # logger.info(p_split)
                phone_number = p_split[2].replace('Phone #', '').replace('Phone#', '').strip()
                if len(phone_number) > 15:
                    phone_number = phone_number[:-8]
                # logger.info(phone_number)
                if 'Business Hours:' in p_split:
                    ind = p_split.index('Business Hours:')
                    hours = ''
                    for h in p_split[ind + 1:]:
                        hours += h + ' '
                    hours = hours.strip()
                else:
                    hours = '<MISSING>'
                # logger.info(hours)
                country_code = 'US'
                if 'Distribution' in location_name:
                    location_type = 'distribution center'
                else:
                    location_type = 'store'

                lat = '<MISSING>'
                longit = '<MISSING>'

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

def fetch_data():
    driver = SgSelenium().chrome()
    locator_domain = 'http://buylowmarket.com/'
    ext = 'locations'

    driver.get(locator_domain + ext)

    # Begin scraper

    targets = ['#settings', '#profile', '#messages', '#home']
    all_store_data = []

    nav = driver.find_element_by_css_selector('ul.nav')
    lis = nav.find_elements_by_css_selector('li')
    for i, li in enumerate(lis):
        logger.info(i)
        li.click()
        get_info(driver, targets[i], locator_domain, all_store_data)

    driver.quit()

    no_dup_data = []
    dup_seen = False
    for data in all_store_data:
        if 'Distribution' in data[1]:
            if not dup_seen:
                no_dup_data.append(data)
                dup_seen = True
        else:
            no_dup_data.append(data)

    return no_dup_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
