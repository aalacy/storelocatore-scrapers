import requests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    base_link = "http://jackscarpet.com/texas/webster/carpet-store.php"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    req = requests.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, 'html.parser')
    
    data = []
    locator_domain = "jackscarpet.com"
    location_name = base.find('h1').text.strip()
    raw_data = str(base.find('address')).strip().split("<br/>")
    street_address = raw_data[0][raw_data[0].find(">")+1:]
    city = raw_data[1][:raw_data[1].find(',')].strip()
    state = raw_data[1][raw_data[1].find(',')+1:raw_data[1].rfind(' ')].strip()
    zip_code = raw_data[1][raw_data[1].rfind(' ')+1:].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = base.find('span', attrs={'id': 'phone-desktop'}).text.strip()
    location_type = location_name[:location_name.rfind(',')].strip()
    hours_of_operation = base.find('ul', attrs={'style': 'list-style:none; font-size:14px; padding-left:15px;'}).get_text(separator=' ').replace("\n"," ").replace("  "," ").strip()
    hours_of_operation = re.sub(' +', ' ', hours_of_operation)
    link = base.find('iframe')['src']

    req = requests.get(link, headers=headers)

    base = BeautifulSoup(req.text,"lxml")

    base_str = str(base)
    base_str = base_str[-508:-480]
    start_point = base_str.find("[") + 1
    latitude = base_str[start_point:base_str.find(",")]
    longitude = base_str[base_str.find(",")+1:base_str.find(']]')]
    
    data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
