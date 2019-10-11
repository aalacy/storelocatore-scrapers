import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import json
import pandas as pd

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
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    canada_states = ['AB', 'BC', 'MB', 'NB', 'NL', 'NT', 'NS', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']
    data = []
    driver.get("https://www.skyzone.com/locations/")
    time.sleep(10)
    req_json = driver.execute_script("return window.SkyZone.locations")
    df = pd.DataFrame(
        columns=['Latitude', 'Longitude', 'City', 'id', 'Street_address', 'Name', 'PhoneNumber', 'postalCode', 'State',
                 'URL', 'hours_of_operation', 'Page_url'])
    count = 0
    for i in req_json:
        if i['status'] == 'coming_soon' or i['status'] == 'closed':
            pass
        else:
            lat = i['latitude']
            lon = i['longitude']
            street_addr = i['street_address']
            location_name = i['name']
            phone = i['phone']
            city = i['city']
            state = i['state']
            zipcode = i['postal_code']
            store_id = i['id']
            url = "https://www.skyzone.com" + i['home_path']
            page_url = 'https://www.skyzone.com/locations/'
            if (street_addr == ""):
                street_addr = '<MISSING>'
            if (city == ""):
                city = '<MISSING>'
            if (zipcode == ""):
                zipcode = '<MISSING>'
            if (phone == ""):
                phone = '<MISSING>'
            if (state == ""):
                state = '<MISSING>'
            try:
                driver2.get(url)
                # time.sleep(10)
                tim = driver2.find_element_by_xpath(
                    "(//a[contains(@class,'hero-details__detail-item')][contains(@href,'hours')])").get_attribute(
                    'textContent').strip()
                hours_of_op = tim
            except:
                hours_of_op = '<MISSING>'
                'NoSuchElementException'
            li = pd.DataFrame(
                [[lat, lon, city, store_id, street_addr, location_name, phone, zipcode, state, url, hours_of_op, page_url]],
                columns=['Latitude', 'Longitude', 'City', 'id', 'Street_address', 'Name', 'PhoneNumber', 'postalCode',
                         'State', 'URL', 'hours_of_operation','Page_url'])
            df = df.append(li)
            df.reset_index(inplace=True, drop=True)
            try:
                loc_type = df.iloc[i]['LocType']
            except:
                loc_type = '<MISSING>'
            data.append([
                'https://www.skyzone.com/',
                page_url,
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
            count = count + 1
            print(count)

    for i in range(len(data)):
        try:
            if (data[i][5] in canada_states):
                data[i][7] = 'CA'
                print(i)
        except:
            'TypeError'

    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()




