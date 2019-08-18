import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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

def parse_address(adr):
    city = adr.split(',')[0]
    state_zip = adr.split(',')[1]
    state = state_zip.rsplit(' ', 1)[0]
    zipcode = state_zip.rsplit(' ', 1)[1]
    return city, state, zipcode

def fetch_data():
    # Your scraper here
    data=[]
    driver.get("http://nypdpizzeria.com/locations.html")
    stores = driver.find_elements_by_css_selector('p.map4')
    for store in stores:
        details = store.text
        details = details.splitlines()
        location_name = details[0]
        street_address = details[1]
        street_address2 = details[2]
        city,state,zipcode = parse_address(street_address2)
        phone = details[3]
        data.append([
             'http://nypdpizzeria.com/',
              location_name,
              street_address,
              city,
              state,
              zipcode,
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