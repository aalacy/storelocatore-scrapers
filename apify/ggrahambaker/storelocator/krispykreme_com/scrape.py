import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://krispykreme.com/'
    ext = 'locate/all-locations'

    driver = get_driver()
    driver.get(locator_domain + ext)

    main_div = driver.find_element_by_css_selector('div.locations')
    locs = main_div.find_elements_by_css_selector('li')
    link_list = []
    for loc in locs:
        link = loc.find_element_by_css_selector('a').get_attribute('href')
        
        if len(link) < 25:
            continue

        if '%' in link:
            continue

        if 'coming-soon' in link:
            continue

        if link in link_list:
            continue

        link_list.append(link)
    

    all_store_data = []
    for link in link_list:
        print(link)
        driver.get(link)
        driver.implicitly_wait(20)

        map_div = driver.find_element_by_css_selector('div#shop-map')
        lat = map_div.get_attribute('data-lat')
        longit = map_div.get_attribute('data-lng')

        cont = driver.find_element_by_css_selector('div.shop-block.shop-location')
        location_name = cont.find_element_by_css_selector('strong.title').text
        street_address = cont.find_element_by_xpath('//div[@itemprop="streetAddress"]').text.replace('\n', ' ').strip()
        city = cont.find_element_by_xpath('//span[@itemprop="addressLocality"]').text.strip()
        state = cont.find_element_by_xpath('//span[@itemprop="addressRegion"]').text.strip()
        zip_code = cont.find_element_by_xpath('//span[@itemprop="postalCode"]').text.strip()
        phone_number = driver.find_element_by_xpath("//a[contains(@href, 'tel:')]").get_attribute('href').replace('tel:', '')
        if len(phone_number) < 5:
            phone_number = '<MISSING>'

        hours = driver.find_element_by_css_selector('div.hour-block').text.replace('\n', ' ').replace('STORE HOURS:', '').strip()


        country_code = 'US'
        page_url = link
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)


    print('nice')

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
