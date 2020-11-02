import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ilovechillers_com')




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
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    # Your scraper here
    data=[]
    driver.get("http://ilovechillers.com/locations.php")
    stores = driver.find_elements_by_css_selector('#inner-wrap > div:nth-child(6) > div.row > div > div')
    for store in stores:
        try:
            location_name = store.find_element_by_css_selector('h2 > strong').text
            logger.info("location_name", location_name)
            tagged_addr = usaddress.tag(store.find_element_by_css_selector('p:nth-child(2)').text)[0]
            try:
                street_address = tagged_addr['AddressNumber'] + " " + tagged_addr['StreetNamePreDirectional'] + " " + tagged_addr['StreetName'] + " " + tagged_addr['IntersectionSeparator'] + " " + tagged_addr['SecondStreetName'] + " " + tagged_addr['SecondStreetNamePostType']
            except:
                try:
                    street_address = tagged_addr['AddressNumber'] + " " + tagged_addr['StreetName'] + " " + tagged_addr['StreetNamePostType'].split('\n')[0]
                except:
                    try:
                        street_address = tagged_addr['AddressNumber'] + " " + tagged_addr['StreetNamePreType'] + " " + tagged_addr['StreetName'].split('\n')[0]
                    except:
                        street_address = tagged_addr['AddressNumber'] + " " + tagged_addr['StreetNamePreDirectional'] + " " + tagged_addr['StreetName']+ " " + tagged_addr['StreetNamePostType'].split('\n')[0]
            city = tagged_addr['PlaceName']
            state = tagged_addr['StateName']
            zipcode = tagged_addr['ZipCode']
            zipcode = re.sub(r'\n', "", zipcode)
            phone = tagged_addr['OccupancyIdentifier']
            phone = re.sub(r'[+]', "", phone)
            logger.info("phone", phone)
            hours_of_op = store.find_element_by_css_selector('p:nth-child(4)').text
            if hours_of_op == " ":
                hours_of_op = store.find_element_by_css_selector('p:nth-child(3)').text
            data.append([
                'http://ilovechillers.com/',
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
                hours_of_op
            ])
        except:
            pass

    geomaps = driver.find_elements_by_xpath("//a[contains(@href, 'https://www.google.com')]")
    i = 0
    while i < len(data):
        lat, lon = parse_geo(geomaps[i].get_attribute('href'))
        data[i][10] = lat
        data[i][11] = lon
        i += 1

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
