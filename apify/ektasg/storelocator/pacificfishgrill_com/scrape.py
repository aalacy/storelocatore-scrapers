import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress
import re

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    count=0
    driver.get("https://www.pacificfishgrill.com/")
    stores = driver.find_elements_by_css_selector('div.pm-map-wrap.pm-location-search-list > div.row')
    page_url = "https://www.pacificfishgrill.com/"
    for store in stores:
            location_name = store.find_element_by_css_selector('div > p:nth-child(1)').text.splitlines()[0]
            print("location_name........" , location_name)
            address = store.find_element_by_css_selector('div > p:nth-child(1) > a:nth-child(2)').text
            tagged = usaddress.tag(address)[0]
            state = tagged['StateName']
            city = tagged['PlaceName']
            zipcode = tagged['ZipCode']
            try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + \
                              tagged['StreetNamePostType'].split('\n')[0]+ " " + \
                              tagged['OccupancyType'] + " " + tagged['OccupancyIdentifier'].split('\n')[0]
            except:
                try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                  tagged['StreetNamePostType'].split('\n')[0] + " " + tagged['OccupancyIdentifier'].split('\n')[0]
                except:
                     street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                                  tagged['StreetNamePostType'].split('\n')[0] + " " + \
                                                  tagged['OccupancyType'] + " " + tagged['OccupancyIdentifier'].split('\n')[0]
            geomap = store.find_element_by_css_selector('div > p:nth-child(1) > a:nth-child(2)').get_attribute('href')
            driver2.get(geomap)
            time.sleep(5)
            lat,lon = parse_geo(driver2.current_url)
            phone =store.find_element_by_css_selector('div > p:nth-child(2)').text
            hours_of_op = store.find_element_by_css_selector('div > div.hours').text
            data.append([
                 'https://www.pacificfishgrill.com/',
                  page_url,
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
                  hours_of_op
                ])
            count+=1
            print(count)

    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()