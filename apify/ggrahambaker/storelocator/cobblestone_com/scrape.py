import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

fields = ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"]
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(fields)
        # Body
        for row in data:
            writer.writerow(row)


def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


MISSING = '<MISSING>'


def get(data, key):
    return data.get(key) or MISSING


def extract(location):
    page_url = get(location, 'url')
    location_name = get(location, 'post_title')
    location_type = MISSING
    store_number = get(location, 'ID')
    phone = get(location, 'phone')

    street_address = get(location, 'address')
    city = get(location, 'city')
    state = get(location, 'state')
    postal = get(location, 'zip')
    country_code = get(location, 'country')
    latitude = get(location, 'lat')
    longitude = get(location, 'lng')

    hours_of_operation = get_hours(page_url)

    return {
        'locator_domain': 'cobblestone.com',
        'page_url': page_url,
        'location_name': location_name,
        'location_type': location_type,
        'store_number': store_number,
        'phone': phone,
        'street_address': street_address,
        'city': city,
        'state': state,
        'zip': postal,
        'country_code': country_code,
        'latitude': latitude,
        'longitude': longitude,
        'hours_of_operation': hours_of_operation
    }


def get_hours(page_url):
    choices = ['Full Service', 'Express Service', 'Oil And Lube', 'Covenience Store', 'Gas Station']
    page = session.get(page_url).text
    soup = BeautifulSoup(page)

    hours = soup.select_one('.location__hours')

    for choice in choices:
        nav_string = hours.find(text=re.compile(choice, re.IGNORECASE))
        if nav_string:
            hour = nav_string.parent.findNext('dd')
            if hour:
                open_close = hour.get_text().strip()
                if open_close:
                    return re.sub('\n', ',', open_close)

    return MISSING


def fetch_data():
    locator_domain = 'https://cobblestone.com/'
    ext = 'locations/'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    headers = {'User-Agent': user_agent}
    params = {
        'sm-xml-search': 1,
        'query_type': 'all'
    }

    locations = session.get('https://cobblestone.com/', params=params, headers=headers).json()

    for location in locations:
        data = extract(location)
        yield [data[field] for field in fields]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
