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
    street_address = adr.rsplit(',', 3)[0]
    city = adr.rsplit(',', 2)[1]
    state_zip = adr.rsplit(',', 1)[1]
    state = state_zip.split(' ')[1]
    zipcode = state_zip.split(' ')[2]
    return street_address, city, state, zipcode

def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://lionsupermarket.com/locations.html")
    stores = driver.find_elements_by_css_selector('div#pu2207 > div.clearfix.grpelem')
    for store in stores:
        store_id = store.get_attribute('id')
        if store_id != 'u1161-4':
            store_id_initials = store_id.split('-')[0]
            location_name = store.find_element_by_css_selector('p#'+store_id_initials+'-2').text
            address = store.find_element_by_css_selector('p#'+store_id_initials+'-4').text
            street_address, city, state, zipcode = parse_address(address)
            hours_of_operation = store.find_element_by_css_selector('p#' + store_id_initials + '-6').text
            phone = store.find_element_by_css_selector('p#' + store_id_initials + '-8').text
            data.append([
                'https://lionsupermarket.com',
                location_name,
                street_address,
                city,
                state,
                zipcode,
                'US',
                store_id,
                phone,
                '<MISSING>',
                '<INACCESSIBLE>',
                '<INACCESSIBLE>',
                hours_of_operation
            ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()