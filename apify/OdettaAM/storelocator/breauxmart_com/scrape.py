import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import requests


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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    # Your scraper here
    data=[]
    #response = requests.get('https://api.freshop.com/1/stores?app_key=breaux_mart&has_address=true&limit=-1&token=f448f7cbfbefb4b7eb6f24bd81be0705')
    response = requests.get('https://api.freshop.com/1/stores?app_key=breaux_mart&has_address=true&limit=-1&token=40343be1840f5a5e915146d700a4f50b')
    time.sleep(3)
    responseJson = json.loads(response.text)
    stores = responseJson.get("items")
    for i in range(len(stores)):
        location_name = stores[i]['name']
        street_address = stores[i]['address_1']
        city = stores[i]['city']
        state = stores[i]['state']
        zipcode = stores[i]['postal_code']
        phone = stores[i]['phone_md'].split('\n')[0]
        hours_of_op = stores[i]['hours_md']
        store_number = stores[i]['store_number']
        latitude = stores[i]['latitude']
        longitude = stores[i]['longitude']
        data.append([
             'https://www.breauxmart.com/',
              location_name,
              street_address,
              city,
              state,
              zipcode,
              'US',
              store_number,
              phone,
              '<MISSING>',
              latitude,
              longitude,
              hours_of_op
            ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
