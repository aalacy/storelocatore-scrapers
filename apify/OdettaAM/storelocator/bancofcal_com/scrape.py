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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body"
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://bancofcal.com/locations/")
    time.sleep(10)
    p = 0 
    stores = driver.find_elements_by_css_selector('div.regColor')
    for store in stores:
        location_name = store.find_element_by_css_selector('h2.mapStoreName > a').text.split('»')[0]
        link = store.find_element_by_css_selector('h2.mapStoreName > a').get_attribute('href')
        raw_address = store.find_element_by_css_selector('p.mapStoreAddress > a').text
        tagged = usaddress.tag(raw_address)[0]
        try:
            try:
                street_addr = tagged['BuildingName'] + " "+ tagged['OccupancyType'] + " " + tagged['OccupancyIdentifier'].split('\n')[0]
            except:
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
                                try:
                                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                                except:
                                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName']
            try:
                state = tagged['StateName'].split(',')[1]
                city = tagged['PlaceName'] + " " + tagged['StateName'].split(',')[0]
            except:
                state = tagged['StateName']
                city = tagged['PlaceName']
            zipcode = tagged['ZipCode']
            geomap = store.find_element_by_css_selector('p.mapStoreAddress > a').get_attribute('href')
            lat, lon = parse_geo(geomap)
            store_id = store.get_attribute('id')
            try:
                phone = store.find_element_by_css_selector('div.mapStorePhoneFax > p:nth-child(1) > a').text
            except:
                phone = '<MISSING>'
            loc_type = store.find_element_by_css_selector('div.mapStoreFeature > p').text
            try:
                hours_of_op = store.find_element_by_css_selector('div.mapStoreBranchTimes').get_attribute('innerHTML')
                hours_of_op = re.sub(r'<ul>|</ul>|<h4>|</h4>|<li>|</li>|&nbsp|\n', "", hours_of_op)
            except:
                hours_of_op = '<MISSING>'
            hours_of_op = hours_of_op.replace('Open:','')
            data.append([
                 'https://bancofcal.com/',
                 link,
                  location_name,
                  street_addr,
                  city,
                  state,
                  zipcode,
                  'US',
                  store_id,
                  phone,
                  loc_type,
                  lat,
                  lon,
                  hours_of_op
                ])
            #print(p,data[p])
            p += 1
        except:
            pass

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
