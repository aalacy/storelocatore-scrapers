import csv
import os
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0].upper()
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    locator_domain = 'https://clicks.com/'

    req = session.get(locator_domain, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")
    all_store_data = []

    ##Corporate location
    divs = base.find_all(class_='clicks_locat')
    cont = divs[1].find(class_='block')
    content = cont.p.text.replace('(',".(").split('.')
    street_address = content[0]
    city, state, zip_code = addy_ext(content[1])
    phone_number = content[2]

    lat = '<MISSING>'
    longit = '<MISSING>'

    country_code = 'US'
    store_number = '<MISSING>'
    location_type = 'Corporate Office'
    location_name = 'CLICKS Billiards'
    hours = '<MISSING>'

    store_data = [locator_domain, locator_domain, location_name, street_address, city, state, zip_code, country_code,
                  store_number, phone_number, location_type, lat, longit, hours]
    all_store_data.append(store_data)

    places = base.find(class_='clicks_locat')
    links = places.find_all(class_='block')
    href_list = []
    for link in links:
        href_list.append(link.a['href'])

    for link in href_list:
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")
        content = base.find(class_="top-location").text.strip().split('\n')
        location_name = base.find(class_="navigation").h2.text.strip()
        street_address = content[0]
        city, state, zip_code = addy_ext(content[1])
        phone_number = base.find(class_="top-location").a.text.strip()
        hours = base.find(class_="top-location").find_all("h2")[-1].text.replace("Hours:","").replace("\r\n"," ").replace("  "," ").strip()

        lat = '<MISSING>'
        longit = '<MISSING>'

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        store_data = [locator_domain, link, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
