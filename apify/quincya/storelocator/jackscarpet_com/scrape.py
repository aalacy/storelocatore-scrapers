import requests
from bs4 import BeautifulSoup
import csv

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

    try:
        base = BeautifulSoup(req.text,"lxml")
    except (BaseException):
        print '[!] Error Occured. '
        print '[?] Check whether system is Online.'
    

    data = []
    locator_domain = "jackscarpet.com"
    location_name = base.find('h1').text.strip()
    raw_data = base.find('address').encode('utf-8').strip().split("<br/>")
    street_address = raw_data[0][raw_data[0].find(">")+1:]
    city = raw_data[1][:raw_data[1].find(',')].strip()
    state = raw_data[1][raw_data[1].find(',')+1:raw_data[1].rfind(' ')].strip()
    zip_code = raw_data[1][raw_data[1].rfind(' ')+1:].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = base.find('span', attrs={'id': 'phone-desktop'}).text.encode('utf-8').strip()
    location_type = location_name[:location_name.rfind(',')].strip()
    latitude = "<INACCESSIBLE>"
    longitude = "<INACCESSIBLE>"
    hours_of_operation = base.find('ul', attrs={'style': 'list-style:none; font-size:14px; padding-left:15px;'}).text.encode('utf-8').strip()

    data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()