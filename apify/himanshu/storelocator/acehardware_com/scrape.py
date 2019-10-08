import csv
import requests
from bs4 import BeautifulSoup
import re
import http.client
import sgzip
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Firefox(executable_path='./geckodriver', options=options)
    

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        hour1 = str(round(hour, 4))
        return str(hour1) + ":00" + " " + am
        
    else:
        sec=(str(int(str(time / 60).split(".")[1]) * 6)[:2])
        return str(hour) + ":" + sec + " " + am

def fetch_data():
    driver = get_driver()
    base_url = "https://www.acehardware.com"
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 1000
    # MAX_DISTANCE = 500000000
    current_results_len = 0
    coords = search.next_coord()    
    headers  = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
        "content-type":"application/json",
        "accept":"application/json",
    }
    driver.get('https://www.acehardware.com/store-locator')
    cookies = driver.get_cookies()
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
   
    soup = BeautifulSoup(driver.page_source, "lxml")
    while coords:
        print(coords)
        result_coords = []
        try:
            k = s.get("https://www.acehardware.com/api/commerce/storefront/locationUsageTypes/SP/locations?pageSize=1000&filter=geo+near("+str(coords[0])+","+str(coords[0])+",5000000000000)", headers=headers).json()
        except:
            continue
        data = k['items']
        current_results_len = len(data)
        print(current_results_len)
        for val in data:
            kk=''
            for x in val['regularHours']:
                open1= minute_to_hours(int(val['regularHours'][x]['label'].split('-')[0]))
                close = minute_to_hours(int(val['regularHours'][x]['label'].split('-')[1]))
                kk = kk + ' '+ x + ' '+ open1 + ' '+close
            hours_of_operation = (kk)
            locator_domain = base_url
            location_name =  val['name']
            street_address = val['address']['address1']
            city = val['address']['cityOrTown']
            state =  val['address']['stateOrProvince']
            zip =  val['address']['postalOrZipCode']
            country_code = 'US'
            store_number = "<MISSING>"
            phone = val['phone']
            if 'phone' in val:
                phone = val['phone']
            location_type = ''
            latitude = val['geo']['lat']
            longitude = val['geo']['lng']
            result_coords.append((latitude,longitude))
            if street_address in addresses:
                continue
            addresses.append(street_address)
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zip if zip else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation.replace("0:00 AM 0:00 AM","close") if hours_of_operation else '<MISSING>')
            store.append("https://www.acehardware.com/store-locator")
            # print("===", str(store))
            yield store
       
        
        # if current_results_len < MAX_RESULTS:
        #     # print("max distance update")
        #     search.max_distance_update(MAX_DISTANCE)
        if current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()
        

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
