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
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://www.cnbbank.bank/who-we-are/locations/")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.col-sm-4.col-md-3.map-item')

    for store in stores:
        location_name = store.find_element_by_css_selector('h3 > a').text
        lat = store.get_attribute('data-lat')
        lon = store.get_attribute('data-lng')
        phone = store.find_element_by_css_selector('p:nth-child(3) > a').text
        raw_address =  store.get_attribute('data-locname')
        tagged = usaddress.tag(raw_address)[0]
        try:
            street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType']
        except:
             try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostDirectional'] + " " +tagged['StreetNamePostType']
             except:
                 try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostDirectional']
                 except:
                     try:
                         street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType']
                     except:
                         street_addr = tagged['BuildingName'] + " " + tagged['OccupancyType'] + " " + tagged['OccupancyIdentifier'] + " " + tagged['StreetNamePreType'].split('br>')[0] + " " + " " + tagged['StreetNamePreType'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType']

        street_addr = street_addr.replace('br>' ,'')
        state = tagged['StateName']
        city = tagged['PlaceName']
        zipcode = tagged['ZipCode']
        data.append([
             'https://www.cnbbank.bank/',
              location_name,
              street_addr,
              city,
              state,
              zipcode,
              'US',
              '<MISSING>',
              phone,
              '<MISSING>',
              lat,
              lon,
              '<MISSING>'
            ])

    name = [stores[i].find_element_by_css_selector('h3 > a').get_attribute('href') for i in range(0, len(stores))]
    for i in range(0, len(name)):
        driver.get(name[i])
        time.sleep(10)
        try:
            hours_of_ops = driver.find_elements_by_css_selector('div.col-sm-4')
            if hours_of_ops == []:
                hours_of_ops = driver.find_elements_by_css_selector('table.table.table-hours')
            hours_of_op = ""
            for j in range(0,len(hours_of_ops)):
                hours_of_op = hours_of_op + hours_of_ops[j].text
        except:
            hours_of_op = '<MISSING>'
        data[i][12] = hours_of_op

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()