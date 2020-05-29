import csv
import os
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }
    locator_domain = 'https://www.wyndhamhotels.com/laquinta/'
    ext = 'locations'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    main = soup.find('div', {'class': 'aem-rendered-content'})
    hrefs = main.find_all("a")
    link_list = []
    base_url = 'https://www.wyndhamhotels.com'
    for h in hrefs:
        if 'overview' in h['href']:
            link_list.append(base_url + h['href'])

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        try:
            loc_j = soup.find('script', {'type': "application/ld+json"}).text
        except:
            continue
        loc_json = json.loads(loc_j)

        lat = loc_json['geo']['latitude']
        longit = loc_json['geo']['longitude']
        country_name = loc_json['address']['addressCountry']
        if 'Mexico' in country_name:
            break

        if 'United States' in country_name:
            country_code = 'US'
        else:
            country_code = 'CA'

        location_name = loc_json['name']
        zip_code = loc_json['address']['postalCode']

        city = loc_json['address']['addressLocality']

        street_address = loc_json['address']['streetAddress']

        state = loc_json['address']['addressRegion']

        phone_number = loc_json['telephone']

        page_url = link
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
