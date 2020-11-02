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
def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    #Variables
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('http://fridarestaurant.com/locations/')
    time.sleep(6)
    # Fetch stores
    name = driver.find_elements_by_tag_name('h4')
    location_name = [name[i].text for i in range(0,len(name))]
    stores = driver.find_elements_by_xpath("//a[contains(@href, 'https://www.google.com')]")
    phones = driver.find_elements_by_xpath("//a[contains(@href, 'tel:')]")
    phone = [phones[i].text for i in range(0,len(phones))]
    for i in range(0,len(stores)-2):
        lat,lon = parse_geo(stores[i].get_attribute('href'))
        latitude.append(lat)
        longitude.append(lon)
        tagged=usaddress.tag(stores[i].text)[0]
        zipcode.append(tagged['ZipCode'])
        state.append(tagged['StateName'])
        city.append(tagged['PlaceName'])
        street_address.append(tagged['AddressNumber']+" "+tagged['StreetName']+" "+tagged['StreetNamePostType'])
    #Fetch more locations from JS variable wpgmaps_localize_marker_data, It doesn't contain phone data. 
    names = driver.execute_script('return wpgmaps_localize_marker_data')
    title = re.findall(r"title': u'(.+?('))", str(names))
    address = re.findall(r"address': u'(.+?('))", str(names))
    lat = re.findall(r"lat': u'(.+?('))", str(names))
    lng = re.findall(r"lng': u'(.+?('))", str(names))
    for i in range(0,len(title)):
        if 'coming soon' not in (title[i][0]):
            try:
                tagged1=usaddress.tag(address[i][0].replace("'",""))[0]
            except:
                tagged1=usaddress.tag(str(address[i][0].replace("'","").split(",")[0:2]))[0]
            if tagged1['ZipCode'] not in zipcode:
                location_name.append(title[i][0].replace(",",""))
                latitude.append(lat[i][0].replace("'",""))
                longitude.append(lng[i][0].replace("'",""))
                zipcode.append(tagged1['ZipCode'].replace("']",""))
                state.append(tagged1['StateName'])
                city.append(tagged1['PlaceName'])
                street_address.append(tagged1['AddressNumber']+" "+tagged1['StreetName']+" "+tagged1['StreetNamePostType'])
                phone.append('<MISSING>')
    for n in range(0,len(location_name)): 
        data.append([
            'https://www.fridarestaurant.com',
            location_name[n],
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
            '<INACCESSIBLE>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
