import csv
import os
from sgselenium import SgSelenium
import re



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def script_search(scripts, driver):
    for s in scripts:
        cont = s.get_attribute('innerHTML')
        if 'var gmwMapObjects' in cont:
            return driver.execute_script('return gmwMapObjects')


def fetch_data():
    locator_domain = 'https://www.xtendbarre.com/'
    ext = 'find-a-studio/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, '/find-a-studio/?country')]")

    link_list = []
    for href in hrefs:
        link = href.get_attribute('href')
        if 'country=699' in link:
            link_list.append(link)
            break
        link_list.append(link)

    store_links = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        links = driver.find_elements_by_css_selector('a.promotion')
        for l in links:
            store_links.append([l.get_attribute('href'), l.text])

    all_store_data = []
    for data in store_links:
        driver.get(data[0])
        driver.implicitly_wait(10)

        page_url = data[0]
        location_name = data[1]

        addy_arr = driver.find_element_by_css_selector('span.address').text.split('/')

        street_address = addy_arr[0].strip()
        if len(addy_arr) == 5:
            street_address += ' ' + addy_arr[1].strip()
            off = 1
        else:
            off = 0
        city_state = addy_arr[1 + off].split('\n')
        city = city_state[0].strip()
        if city == '':
            city = "Brooklyn"
        state = city_state[1].strip()
        zip_code = addy_arr[2 + off].strip()

        if 'United' in addy_arr[3 + off]:
            country_code = 'US'
        else:
            country_code = 'CA'



        phone_number = driver.find_element_by_css_selector('span.add_info.phone').find_element_by_css_selector('a').text


        scripts = driver.find_elements_by_xpath('//script[@type="text/javascript"]')

        map_obj_str = str(script_search(scripts, driver))

        result_lat = re.search(r"'lat': '\d+\.?\d*',", map_obj_str).group(0)
        result_lng = re.search(r"'lng': '-\d+\.?\d*',", map_obj_str).group(0)

        lat = result_lat.split(':')[1].strip()[1:-2]
        longit = result_lng.split(':')[1].strip()[1:-2]



        store_number = '<MISSING>'
        location_type = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
