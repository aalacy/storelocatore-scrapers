import csv
import os
from sgselenium import SgSelenium
import time
from selenium.webdriver.support.wait import WebDriverWait
import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def request_wrapper(url,method,headers,data=None):
   request_counter = 0
   if method == "get":
       while True:
           try:
               r = requests.get(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   elif method == "post":
       while True:
           try:
               if data:
                   r = requests.post(url,headers=headers,data=data)
               else:
                   r = requests.post(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   else:
       return None
def fetch_data():
    addressess = []
    main_array=[]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    base_url = "http://singaspizzas.com/"
    location_url = "https://api.ordersnapp.com/v2/stores?brand_id=141"
    r = request_wrapper(location_url,"get",headers=headers).json()
    data = (r['data']['stores'])
    for i in data:
        phone = (i['phone'])
        location_name = (i['name'])
        street_address = (i['address']['street_1']).replace('     ',"").lower().replace("-","").strip().replace("4202 northern boulevard","4202 northern blvd.").replace('26021 hillside avenue',"26021 hillside ave")
        city =(i['address']['city'])
        state = (i['address']['region'])
        zipp = (i['address']['postal_code'])
        country_code = i['country']
        store_number = i['address']['addressable_id']
        location_type = i["brand_name"]
        latitude = (i['address']['latitude'])
        longitude =(i['address']['longitude'])
        hours_of_operation = str(i['hours']).replace("{","").replace("}","").replace("'","").replace("sunday: open: , close: ","sunday: open: closed , close: closed ")
        page_url =  "https://singasgrill.ordersnapp.com/home?external_store_id="+str(store_number)
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name.replace('**FLUSHING NY**','FLUSHING NY') if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else"<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        main_array.append(store)
        # yield store
    locator_domain = 'http://singaspizzas.com/'
    ext = 'locations/'
    driver =get_driver()
    driver.get(locator_domain + ext)
    stores = driver.find_elements_by_css_selector('div.et_pb_text.et_pb_module.et_pb_text_align_left')
    all_store_data = []
    for store in stores:
        content = store.text.split('\n')
        if len(content) > 1:
            location_name = content[0]
            street_address = content[1].replace("4202 northern boulevard","4202 northern blvd.")
            city = content[2]
            zip_code = content[3]
            phone_number = content[-1]
            state = '<MISSING>'
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            hours = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            page_url = "http://singaspizzas.com/locations/"
            if "Corona NY" in location_name:
                city = city.split(",")[0]
                state = "NY"
                zip_code = "11368"
            store_data = [locator_domain, location_name, street_address.lower().replace("-","").replace("4202 northern boulevard","4202 northern blvd.").replace("41 dock","41 dock street").replace('26021 hillside avenue',"26021 hillside ave"), city, state, zip_code, country_code,
                          store_number,phone_number, location_type, lat, longit, hours,page_url]
            main_array.append(store_data)
            # yield store_data
    driver.quit()

   
    for q in range(len(main_array)):
        if main_array[q][2] in addressess:
            continue
        addressess.append(main_array[q][2])
        yield main_array[q]
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
