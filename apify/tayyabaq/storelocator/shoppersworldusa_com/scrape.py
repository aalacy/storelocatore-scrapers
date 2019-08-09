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
    a=re.findall(r'\&ll=(-?[\d\.]*,(--?[\d\.]*))',url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
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
    driver.get('http://shoppersworldusa.com/store.html')
    time.sleep(6)
    # Fetch stores
    stores = driver.find_elements_by_class_name("maincontent")
    loc = stores[0].text.split("\n")
    for i in range(0,len(loc)):
        if loc[i]!="":
            a=re.findall("[\d].*[\Q\s][A-Z].*",loc[i])
            try:
                street_address.append(a[0].split(",")[0])
                b=re.findall("[\d].*",a[0].split(",")[1].strip())
                if b!=[]:
                    city.append('<INACCESSIBLE>')
                else:
                    city.append(a[0].split(",")[1].strip())
                state.append(re.findall("([A-Z]{2}) (\d{5})",loc[i])[0][0])
                try:
                    zipcode.append(re.findall("([A-Z]{2}) (\d{5})",loc[i])[0][1])
                except:
                    zipcode.append('<MISSING>')
                try:
                    phone.append(re.findall(r'([(]-?[\d\.]*?.*)',loc[i])[0].split(",")[0])
                except:
                    phone.append('<MISSING>')
                try:
                    location_name.append(loc[i].split(",")[-4])
                except:
                    location_name.append('<MISSING>')
            except:
                continue
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
            '<MISSING>',
            '<MISSING>',
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
    
scrape()
