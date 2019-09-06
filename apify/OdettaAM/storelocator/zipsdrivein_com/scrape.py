import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'2d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    lat = re.findall(r'3d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data = []
    driver.get("http://zipsdrivein.com/locations.html")
    time.sleep(10)
    stores1 = driver.find_elements_by_css_selector('table > tbody > tr > td > div > table:nth-child(3) > tbody > tr > td:nth-child(1) > p')
    stores2 = driver.find_elements_by_css_selector('table > tbody > tr > td > div > table:nth-child(3) > tbody > tr > td:nth-child(2) > p')
    stores3 = driver.find_elements_by_css_selector('table > tbody > tr > td > div > table:nth-child(3) > tbody > tr > td:nth-child(3) > p')
    stores = stores1 + stores2 + stores3
    for store in stores:
        info = store.text
        li = info.splitlines()
        if len(li) ==4:
            location_name = li[0]
            if location_name == '**NEW LOCATION**':
                location_name = li[1]
                street_addr = li[2]
                state = li[3].split(',')[1]
                city = li[3].split(',')[0]
                phone = '<MISSING>'
            else:
                street_addr = li[1]
                state = li[2].split(',')[1]
                city = li[2].split(',')[0]
                phone = li[3]
        elif len(li) ==3:
            location_name = '<MISSING>'
            street_addr = li[0]
            state = li[1].split(',')[1]
            city = li[1].split(',')[0]
            phone = li[2]
        elif len(li) ==5:
            location_name = li[0]
            street_addr = li[1]
            state = li[2].split(',')[1]
            city = li[2].split(',')[0]
            phone = li[3]
        data.append([
                     'http://zipsdrivein.com/',
                      location_name,
                      street_addr,
                      city,
                      state,
                      '<MISSING>',
                      'US',
                      '<MISSING>',
                      phone,
                      '<MISSING>',
                      '<MISSING>',
                      '<MISSING>',
                      '<MISSING>'
                 ])

    time.sleep(3)
    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()