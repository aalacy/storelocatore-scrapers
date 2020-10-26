import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from random import randint

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'http://www.brigantine.com/'

    driver = get_driver()
    time.sleep(2)

    driver.get(locator_domain)

    locs = driver.find_elements_by_css_selector('.location')
    all_store_data = []
    for i in range (len(locs)):
        driver.get(locator_domain)
        locs = driver.find_elements_by_css_selector('.location')
        loc = locs[i]
        cont = loc.text.split('\n')
        if "coming soon" in cont[0].lower():
            continue
        location_name = cont[0].split('(')[0].strip()
        print(location_name)
        phone_number = cont[1]
        street_address = cont[2]
        city = cont[3].replace(",","")
        state = cont[4]
        zip_code = cont[5]
        hours_div = loc.find_element_by_xpath('//div[@class="list-location"]')
        hours_html = driver.execute_script("return arguments[0].innerHTML", hours_div)
        soup = BeautifulSoup(hours_html, 'html.parser')

        hours = soup.text.replace('\n', ' ').strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        try:
            gmaps_link = loc.find_element_by_css_selector(".directions").find_element_by_tag_name('a').get_attribute('href')
            if "maps" in gmaps_link:
                driver.get(gmaps_link)
                time.sleep(randint(6,8))

                map_link = driver.current_url
                at_pos = map_link.rfind("@")

                if at_pos < 0:
                    time.sleep(randint(4,6))

                map_link = driver.current_url
                at_pos = map_link.rfind("@")

                latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
                longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()

            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        store_data = [locator_domain, locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, latitude, longitude, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
