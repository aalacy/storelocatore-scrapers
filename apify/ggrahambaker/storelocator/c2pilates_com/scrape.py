import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.c2pilates.com/'

    page = session.get(locator_domain)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    divs = soup.find_all('div', {'itemtype': 'http://schema.org/LocalBusiness'})
    all_store_data = []

    for div in divs:
        location_name = div.find('h4').text

        street_address = div.find('span', {'itemprop': 'streetAddress'}).text

        city = div.find('span', {'itemprop': 'addressLocality'}).text
        state = div.find('span', {'itemprop': 'addressRegion'}).text
        zip_code = div.find('span', {'itemprop': 'postalCode'}).text
        phone_number = div.find('span', {'itemprop': 'telephone'}).text
        lat = div.find('meta', {'itemprop': 'latitude'})['content']
        if lat == '':
            lat = '<MISSING>'
            longit = '<MISSING>'

        longit = div.find('meta', {'itemprop': 'longitude'})['content']

        country_code = 'US'
        store_number = '<MISSING>'
        hours = '<MISSING>'

        split_locs = street_address.split('   ')
        if len(split_locs) == 2:
            for sp in split_locs:
                sp_add = sp.split(':')
                location_type = sp_add[0]
                street_address = sp_add[1].strip()
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)
        else:
            location_type = '<MISSING>'
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    return  all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
