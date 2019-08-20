import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://www.craftrepublic.com/locations/")
    stores = driver.find_elements_by_css_selector('a.locationLink')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    for i in range(0, len(name)):
        driver.get(name[i])
        time.sleep(5)
        location_name = driver.find_element_by_css_selector('div.locationAddress > h2').text
        raw_address = driver.find_element_by_css_selector('div.locationAddress > p').text
        tagged = usaddress.tag(raw_address)[0]
        try:
            street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0] + " " + tagged['OccupancyType'] + " " + tagged['OccupancyIdentifier'].split('\n')[0]
        except:
            try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
            except:
                try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostDirectional'].split('\n')[0] + " " +tagged['StreetNamePostType'].split('\n')[0]
                except:
                    try:
                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostDirectional'].split('\n')[0]
                    except:
                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
        state = tagged['StateName']
        city = tagged['PlaceName']
        zipcode = tagged['ZipCode']
        phone = driver.find_element_by_css_selector('a.locationLink').text
        hours_of_op = driver.find_element_by_css_selector('div.locationHours > p').text
        data.append([
             'https://www.craftrepublic.com/',
              location_name,
              street_addr,
              city,
              state,
              zipcode,
              'US',
              '<MISSING>',
              phone,
              '<MISSING>',
              '<INACCESSIBLE>',
              '<INACCESSIBLE>',
              hours_of_op
            ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()