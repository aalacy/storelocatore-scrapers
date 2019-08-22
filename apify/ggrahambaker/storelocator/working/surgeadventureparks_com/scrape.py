import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


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

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def cut(arr):
    for i, a in enumerate(arr):
        if 'Surge' in a and 'Park' in a:
            return i



def fetch_data():
    locator_domain = 'http://www.surgeadventureparks.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    element_to_hover_over = driver.find_element_by_xpath("//li[contains(text(),'Locations')]")

    hover = ActionChains(driver).move_to_element(element_to_hover_over)
    hover.perform()

    ul = driver.find_element_by_css_selector('ul.sub_left')
    lis = ul.find_elements_by_css_selector('li')
    link_list = []
    for li in lis:
        if 'm//' in li.find_element_by_css_selector('a').get_attribute('href'):
            break
        link_list.append(li.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link + 'ContactUs')
        driver.implicitly_wait(10)
        main = driver.find_element_by_css_selector('div.ContentZoneContent')

        content = main.text.split('\n')
        c_cont = content[cut(content):]

        if len(c_cont) == 14:
            street_address = c_cont[1] + ' ' + c_cont[2]
            city, state, zip_code = addy_ext(c_cont[3])
            base = 1
        else:
            street_address = c_cont[1]
            city, state, zip_code = addy_ext(c_cont[2])
            base = 0

        if len(zip_code) == 4:
            zip_code = '23602'

        phone_number = c_cont[base + 3].replace('Telephone:', '').replace('Telephone', '').strip()

        hours = ''
        for h in c_cont[base + 6:]:
            hours += h + ' '

        hours = hours.strip()

        src = driver.find_element_by_css_selector('iframe').get_attribute('src')

        start = src.find('!2d')
        end = src.find('!3m2')
        if start > 1:
            coords = src[start + 3: end].split('!3d')
            lat = coords[1][:9]
            longit = coords[0][:8]
        else:
            lat = '<MISSING>'
            longit = '<MISSING>'

        location_name = link[link.find('s/') + 2: -1]

        store_number = '<MISSING>'
        location_type = '<MISSING>'
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
