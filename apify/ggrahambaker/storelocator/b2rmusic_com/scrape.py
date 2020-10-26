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
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1].replace('.', '')
        zip_code = prov_zip[2]

    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.b2rmusic.com/'
    ext = 'browse-locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    rows = driver.find_elements_by_css_selector('tr.row')
    link_arr = []
    for row in rows:
        # print(row.find_element_by_css_selector('a').get_attribute('href'))
        link_arr.append(row.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_arr:
        driver.implicitly_wait(10)
        driver.get(link)
        loc_business = driver.find_element_by_xpath("//div[@itemtype='http://schema.org/LocalBusiness']")

        content = loc_business.text.split('\n')
        phone_number = content[0].replace('Phone: ', '')
        # weird case
        if '781-943-3944' in phone_number:
            street_address = content[3] + ' ' + content[4]
            city, state, zip_code = addy_extractor(content[5])

        else:
            street_address = content[3]
            city, state, zip_code = addy_extractor(content[4])
        location_name = city

        hours = ''
        for h in content[6:]:
            hours += h + ' '
        hours = hours.replace('Hours of Operation', '').strip()

        a_tags = loc_business.find_elements_by_css_selector('a')
        href = a_tags[2].get_attribute('href')

        start_idx = href.find('/@')
        end_idx = href.find('z/data')
        if start_idx == -1:
            lat = '<INACCESSIBLE>'
            longit = '<INACCESSIBLE>'
        else:
            coords = href[start_idx + 2: end_idx].split(',')
            lat = coords[0]
            longit = coords[1]

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
