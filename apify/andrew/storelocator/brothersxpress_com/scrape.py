import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('/bin/chromedriver', options=options)

BASE_URL = 'http://brothersxpress.com/storelist.html'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def remove_duplicate_white_spaces(string):
    return " ".join(string.split())

def parse_address(address):
    address = remove_duplicate_white_spaces(address)
    _address = [item.strip() for item in address.split(',')]
    state, zipcode = _address[-1].split()
    return _address[0], _address[1], state, zipcode

def fetch_data():
    data = []
    driver.get(BASE_URL)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    stores = soup.select('table table table table tr')[1:]
    for store in stores:
        store_number, location_name, phone, address = [
            td.text
            for td in store.select('td')
        ]
        street_address, city, state, zipcode = parse_address(address)
        phone = remove_duplicate_white_spaces(phone)
        if 'Coming Soon' in phone: continue
        data.append([
            BASE_URL,
            remove_duplicate_white_spaces(location_name),
            street_address,
            city,
            state,
            zipcode,
            'US',
            store_number,
            phone,
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            '<MISSING>'
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
