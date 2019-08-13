import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re


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
    driver.get("http://www.cauldronicecream.com/locations")
    globalvar = driver.execute_script("return jsonContent ;")
    json_data = globalvar['data']
    i = 0
    for i in range(len(json_data)):
        location_name = json_data[i]['title']
        street_address =  json_data[i]['street_number'] + " " + json_data[i]['address_route'] + " " + json_data[i]['subpremise']
        city = json_data[i]['city']
        zipcode = json_data[i]['postal_code']
        country = json_data[i]['country']
        if(country == "" or country == "United States"):
            country_code = "US"
        elif country == "Canada":
            country_code = "CA"
        mod_state = json_data[i]['state']
        if country == "Canada":
            state = mod_state.split(" ")[0]
            zipcode = mod_state.split(" ")[1] + " " + mod_state.split(" ")[2]
        else:
            state = mod_state
        store_number = json_data[i]['id']
        phone  =  json_data[i]['phone']
        if phone == "":
            phone = '<MISSING>'
        latitude = json_data[i]['lat']
        longitude = json_data[i]['lng']
        hours_of_operation = json_data[i]['hours']
        if hours_of_operation == "":
            hours_of_operation = '<MISSING>'
        else:
            hours_of_operation = re.sub(r'<br />|</br>', " ", hours_of_operation)
        data.append([
             'http://www.cauldronicecream.com/',
              location_name,
              street_address,
              city,
              state,
              zipcode,
              country_code,
              store_number,
              phone,
              '<MISSING>',
              latitude,
              longitude,
              hours_of_operation
            ])
        i+=1

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()