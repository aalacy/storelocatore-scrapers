import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def parse_geo(url):
    lon = re.findall(r'\!2d(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\!3d(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('http://nebook.com/contact/')
    time.sleep(3)
    stores=driver.find_elements_by_xpath(("//div[contains(@class,'boc_list_item_text small')]"))
    for n in range(0,len(stores)-3,3):
        tagged = usaddress.tag(stores[n].text)[0]
        try:
            street_address.append(tagged['AddressNumber']+" "+tagged['StreetNamePreDirectional']+" "+tagged['StreetName']+" "+tagged['StreetNamePostType']+" "+tagged['OccupancyType']+" "+tagged['OccupancyIdentifier'])
        except:
            street_address.append(tagged['AddressNumber']+" "+tagged['StreetNamePreDirectional']+" "+tagged['StreetName']+" "+tagged['StreetNamePostType'])
        city.append(tagged['PlaceName'])
        state.append(tagged['StateName'])
        zipcode.append(tagged['ZipCode'])
    for n in range(2,len(stores)-3,3):
        phone.append(stores[n].text)
    googlemap = driver.find_elements_by_xpath(("//div[@class ='wpb_map_wraper']/iframe"))
    geomaps = [googlemap[n].get_attribute('src') for n in range(0,len(googlemap))]
    for n in range(0,len(geomaps)):
        lat, lon = parse_geo(str(geomaps[n]))
        latitude.append(lat)
        longitude.append(lon) 
    for n in range(0,len(street_address)): 
        data.append([
            'http://nebook.com',
            '<MISSING>',
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
