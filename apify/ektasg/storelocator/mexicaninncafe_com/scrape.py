import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import json


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
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("https://www.mexicaninncafe.com/locations")
    page_url = "https://www.mexicaninncafe.com/locations"
    time.sleep(10)
    columns = driver.find_elements_by_css_selector('div.col.sqs-col-4.span-4')
    hours_of_op_all = driver.find_element_by_css_selector('div.sqs-block.html-block.sqs-block-html > div > p:nth-child(2)').text + \
                    "     " + driver.find_element_by_css_selector('div.sqs-block.html-block.sqs-block-html > div > p:nth-child(4)').text
    hours_of_op_all = hours_of_op_all.replace('All Locations (Except North Henderson)',"")
    hours_northhenderson = driver.find_element_by_css_selector('div.sqs-block.html-block.sqs-block-html > div > p:nth-child(3)').text + \
                    "     " + driver.find_element_by_css_selector('div.sqs-block.html-block.sqs-block-html > div > p:nth-child(4)').text
    hours_northhenderson = hours_northhenderson.replace("North Henderson Location","")
    stores = []; gmaps = []

    for column in columns:
        stores1 = column.find_elements_by_css_selector('div.sqs-block.html-block.sqs-block-html')
        for i in range(0,len(stores1)):
            stores.append(stores1[i])
        gmaps1 = column.find_elements_by_css_selector('div.sqs-block.map-block.sqs-block-map')
        for i in range(0,len(gmaps1)):
            gmaps.append(gmaps1[i])

    location_name = [] ; phone = [] ;  lat = [] ; lng =[] ; street_addr = []; zipcode = [] ; state = [] ; city = []
    for store in stores:
        location_name.append(store.find_element_by_css_selector('div > h2').text)
        phone.append(store.find_element_by_css_selector('div > p > a:nth-child(3)').text)


    for gmap in gmaps:
        text = gmap.get_attribute('data-block-json')
        json_data = json.loads(text)
        req_json =json_data['location']
        lat.append(req_json['mapLat'])
        lng.append(req_json['mapLng'])
        street_addr.append(req_json['addressLine1'])
        state_city_zip = req_json['addressLine2']
        zipcode.append(state_city_zip.split(" ")[-1])
        state.append(state_city_zip.split(" ")[-2])
        city.append(state_city_zip.split(",")[0])

    for i in range(0,len(location_name)):
        if location_name[i] =='NORTH HENDERSON':
            hours_of_op = hours_northhenderson
        else:
            hours_of_op = hours_of_op_all
        data.append([
                'https://www.mexicaninncafe.com/',
                page_url,
                location_name[i],
                street_addr[i],
                city[i],
                state[i].replace(',',""),
                zipcode[i],
                'US',
                '<MISSING>',
                phone[i],
                '<MISSING>',
                lat[i],
                lng[i],
                hours_of_op.replace("\n", " ")
            ])
        count = count + 1
        print(count)


    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()