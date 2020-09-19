import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    lon = re.findall(r'\"mapLng":(-?[\d\.]*)', url)[0]
    lat = re.findall(r'\"mapLat":(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('https://www.kayesfoodmarket.com/')
    time.sleep(3)
    a=driver.find_elements_by_xpath(("//div[contains(@id,'block-yui_3_17_2_7_1509469016998')]"))
    for n in range(0,len(a)):
        if a[n].text!='':
            location_name.append(a[n].text.split("\n")[0])
            phone.append(a[n].text.split("\n")[-1])
            street_address.append(a[n].text.split("\n")[1])
            city.append(a[n].text.split("\n")[2].split(",")[0])
            state.append(a[n].text.split("\n")[2].split(",")[1].split()[0].strip())
            zipcode.append(a[n].text.split("\n")[2].split(",")[1].split()[1].strip())
    geomap = driver.find_elements_by_xpath(("//div[contains(@class,'map-block')]"))
    for n in range(0,len(geomap)):
        lat,lon = parse_geo(str(geomap[n].get_attribute('data-block-json')))
        latitude.append(lat)
        longitude.append(lon)
    for n in range(0,len(location_name)): 
        data.append([
            'https://www.kayesfoodmarket.com',
            'https://www.kayesfoodmarket.com/',
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
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
