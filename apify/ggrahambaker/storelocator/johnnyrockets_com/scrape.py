import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.johnnyrockets.com'
    ext = '/locations/'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    hrefs = base.find(id="cg_usa").find_all(class_="all-location-link")

    link_list = []
    for href in hrefs:
        link = locator_domain + href['href']
        link_list.append(link)

    canada_as = base.find(id="cg_canada").find_all(class_="all-location-link")
    for a in canada_as:
        link_list.append(locator_domain + a['href'])

    ships = base.find(id="cg_ship").find_all(class_="all-location-link")
    for ship in ships:
        link_list.append(locator_domain + ship['href'])

    all_store_data = []

    for i, link in enumerate(link_list):
        # print(link)
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        location_name = base.h1.text.strip()

        loc_j = base.find_all('script', attrs={'type': "application/ld+json"})[1]
        loc_json = json.loads(loc_j.text)

        addy = loc_json['address']
        street_address = addy['streetAddress']
        city = addy['addressLocality']
        state = addy['addressRegion']

        zip_code = addy['postalCode']
        if zip_code == '':
            zip_code = '<MISSING>'

        if 'openingHours' in loc_json:
            hours = ''
            hours_list = loc_json['openingHours']
            for h in hours_list:
                hours += h + ' '

            hours = hours.strip()
        else:
            try:
                if "temporarily closed" in base.find(class_="hours_block").text.lower():
                    hours = "Temporarily Closed"
                else:
                    hours = '<MISSING>'
            except:
                hours = '<MISSING>'

        if 'telephone' in loc_json:
            phone_number = loc_json['telephone']
            if "," in phone_number:
                phone_number = phone_number[:phone_number.find(",")].strip()
            if "x" in phone_number:
                phone_number = phone_number[:phone_number.find("x")].strip()
        else:
            phone_number = '<MISSING>'

        geo = base.find(class_='list__item loc_item')
        lat = geo['data-lat']
        longit = geo['data-lon']

        store_number = '<MISSING>'
        location_type = '<MISSING>'

        if 'canada' in link:
            country_code = 'CA'
        else:
            country_code = 'US'

        store_data = [locator_domain, link, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
