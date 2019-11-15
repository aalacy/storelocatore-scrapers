import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url" ,"location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = []
    driver = get_driver()
    driver.get('https://www.speedycash.com/find-a-store/illinois/')
    source = driver.page_source
    script = []
    capture = False
    for line in source.splitlines():
        if "var stores = []" in line:
            capture = True
        elif "initialize_map(stores" in line:
            capture = False
        if capture:
            script.append(line)
    stores = driver.execute_script('\n'.join(script) + "\n return stores2;");
    lat = re.findall(r'addr=(.*?)\%2C', str(stores))
    lon = re.findall(r"%2C(.*?)\',", str(stores))
    street_address = re.findall(r"address': '(.*?)\',", str(stores))
    #street_address = [lat_lon[n].replace("': u'","").split(",")[0] for n in range(1,len(lat_lon))]
    city = re.findall(r"city': '(.*?)\',", str(stores))
    state = re.findall(r"state': '(.*?)\',", str(stores))
    zipcode = re.findall(r"zip': '(.*?)\'}", str(stores))
    print (zipcode)
    phone = re.findall(r"phone': '(.*?)\',", str(stores))
    page_url = re.findall(r"url': '(.*?)\',", str(stores))
    for n in range(0,len(street_address)):
        data.append([
            'https://www.speedycash.com',
            page_url[n],
            'Speedy Cash',
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            lat[n],
            lon[n],
            '<INACCESSIBLE>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
