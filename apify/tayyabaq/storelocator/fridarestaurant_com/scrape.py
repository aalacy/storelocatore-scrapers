import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

def write_output(data):
    with open('data.csv', mode='wb') as output_file:
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
    #Get site
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
        a=stores[i].text.split(".")
        zipcode.append(re.findall("(\d{5})",stores[i].text)[0])
        state.append(re.findall("([A-Z]{2})[,]?",stores[i].text)[0])
        try:
            street_address.append(a[0])
            city.append(a[1].strip().split(",")[0])
        except:
            city.append('<INACCESSIBLE>')
            street_address.append(stores[i].text.split(",")[0])
    
    for n in range(0,len(location_name)): 
        data.append([
            'https://www.crayolaexperience.com',
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
