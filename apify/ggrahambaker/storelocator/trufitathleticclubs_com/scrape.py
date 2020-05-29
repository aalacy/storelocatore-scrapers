import csv
import os
from sgselenium import SgSelenium

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://trufitathleticclubs.com/'
    ext = 'texas/locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    element = driver.find_element_by_xpath('//a[@data-target="#tx"]')
    driver.execute_script("arguments[0].click();", element)

    link_list = []
    hrefs = driver.find_elements_by_xpath("//a[contains(@href, 'trufitathleticclubs.com/texas/clubs?club=')]")
    for href in hrefs:
        link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        location_name = driver.find_element_by_css_selector('h1.loc-title').text.replace('TRUFIT', '').strip()

        info = driver.find_element_by_css_selector('div.infoWrap').find_element_by_css_selector('div.row')

        cont = info.find_elements_by_css_selector('div')[0].text.split('\n')

        street_address = cont[0]
        city, state, zip_code = addy_ext(cont[1])
        phone_number = cont[2]

        hours = ''
        for c in cont[4:]:
            hours += c + ' '

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        page_url = link
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
