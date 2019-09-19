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
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    a=re.findall(r'\?ll=(-?[\d\.]*,(--?[\d\.]*))',url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://www.pabbqgrille.com/locations/")
    time.sleep(10)
    text = driver.find_element_by_xpath("//script[@type='application/ld+json']").get_attribute('innerHTML')
    req_json = json.loads(text)
    json_data = req_json['subOrganization']
    count =0
    for i in range(0,len(json_data)):
        phone = json_data[i]['telephone']
        location_name = json_data[i]['address']['name']
        street_addr = json_data[i]['address']['streetAddress']
        city = json_data[i]['address']['addressLocality']
        state = json_data[i]['address']['addressRegion']
        zipcode = json_data[i]['address']['postalCode']
        loc_type = json_data[i]['@type']
        url = json_data[i]['url']
        driver2.get(url)
        time.sleep(10)
        hours_of_op = driver2.find_element_by_css_selector('#intro > p:nth-child(4)').text
        if hours_of_op == '' or 'Monday' not in hours_of_op:
            hours_of_op = driver2.find_element_by_css_selector('#intro > p:nth-child(5)').text
            if hours_of_op == "" or 'Monday' not in hours_of_op:
                hours_of_op = driver2.find_element_by_css_selector('#intro > p:nth-child(8)').text
        lat = driver2.find_element_by_css_selector('div.gmaps').get_attribute('data-gmaps-lat')
        lon = driver2.find_element_by_css_selector('div.gmaps').get_attribute('data-gmaps-lng')
        data.append([
             'https://www.pabbqgrille.com/',
              location_name,
              street_addr,
              city,
              state,
              zipcode,
              'US',
              '<MISSING>',
              phone,
              loc_type,
              lat,
              lon,
              hours_of_op
            ])
        print(count)
        count+=1

    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()