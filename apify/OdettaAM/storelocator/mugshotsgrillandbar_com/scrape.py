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
    driver.get("https://www.mugshotsgrillandbar.com/maps")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.eapps-google-maps-bar-list-item')
    for store in stores:
        location_name = store.find_element_by_css_selector('div.eapps-google-maps-bar-list-item-info-item.eapps-google-maps-bar-list-item-info-title').text
        address = store.find_element_by_css_selector('div.eapps-google-maps-bar-list-item-info-item-address.eapps-google-maps-bar-list-item-info-item > div').text
        tagged = usaddress.tag(address)[0]
        phone = store.find_element_by_css_selector('div.eapps-google-maps-bar-list-item-info-item-contacts.eapps-google-maps-bar-list-item-info-item > div > a').get_attribute('href').split('tel:')[1]
        phone = re.sub(r'%E2%80%AD|%E2%80%AC', "", phone)
        try:
           street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
        except:
            try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0] + " " + tagged['StreetNamePostDirectional'] + " " + tagged['OccupancyIdentifier']
            except:
                try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                except:
                    try:
                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostDirectional'].split('\n')[0] + " " +tagged['StreetNamePostType'].split('\n')[0]
                    except:
                        try:
                            street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]+ " " + tagged['OccupancyIdentifier'].split('\n')[0]
                        except:
                            try:
                                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                            except:
                                try:
                                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreType'] + " " +tagged['StreetName'] + " " + tagged['StreetNamePostDirectional']
                                except:
                                    try:
                                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName']
                                    except:
                                        street_addr = '<MISSING>'
        try:
            state = tagged['StateName']
        except:
            state = '<MISSING>'
        try:
            city = tagged['PlaceName']
        except:
            city = '<MISSING>'
        try:
            zipcode = tagged['ZipCode']
        except:
            zipcode = '<MISSING>'
        if phone != "COMING SOON" :
            data.append([
                 'https://www.mugshotsgrillandbar.com/',
                  location_name,
                  street_addr,
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