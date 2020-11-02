import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

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
    driver.get('http://atmomed.com/hours-location/')
    time.sleep(6)
    driver.find_element_by_xpath("//div[@id='popmake-1644']/button").click()
    time.sleep(6)
    location =driver.find_elements_by_xpath("//div[@class='wpb_wrapper']/h3")
    location_name = [location[n].text for n in range(0,len(location),2)]
    stores = driver.find_elements_by_xpath("//div[@class='wpb_wrapper']/p[1]")
    address = [stores[n].text for n in range(0,len(stores),2)]
    street_address = [stores[n].text.split("\n")[0] for n in range(0,len(stores),2)]
    phones = driver.find_elements_by_xpath("//a[contains(@href, 'tel:')]")
    phone = [phones[n].text for n in range(0,len(phones))]
    hours_of_operation =[stores[n].text.replace('\u2013',' ') for n in range(1,len(stores),2)]
    googlemap = driver.find_elements_by_css_selector('iframe')
    googlemaps = [googlemap[n].get_attribute('src') for n in range(0,len(googlemap))]
    for n in range(0,len(location_name)):
        a=address[n].split("\n")[1].split()
        if len(a) > 3:
            city.append(str(a[0]+" "+a[1]))
            state.append(a[-2])
            zipcode.append(a[-1])
        else:
            city.append(str(a[0]))
            state.append(a[1])
            zipcode.append(a[2])
        lat, lon = parse_geo(googlemaps[n])
        latitude.append(lat)
        longitude.append(lon)
    for n in range(0,len(location_name)): 
        data.append([
            'http://atmomed.com',
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
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
