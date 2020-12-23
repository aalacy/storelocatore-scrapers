import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
days = ['Sunday', 'Monday', 'Tuesday',
        'Wednesday', 'Thursday', 'Friday', 'Saturday']


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def format_hours(hours_dict):
    formatted = [f'{day}: {hours_dict[day.lower()]["open"]} - {hours_dict[day.lower()]["close"]}' for day in days]
    return ', '.join(formatted)


def get_hours_all_closed():
    # some locations have store hours listed but status 'unavailable'
    # example as of 2020-06-06: https://www.kfc.co.uk/kfc-near-me/bristol-eastgate-retail-park
    hours = [f'{day}: Closed' for day in days]
    return ', '.join(hours)


def get_hours(hours, status):
    # hours argument is a list of dicts
    hours_str = ''

    if status == 'unavailable' or len(hours) == 0:
        hours_str = get_hours_all_closed()
    else:
        # for the store hours, find the dict with type="Standard"
        store_hours = next(
            (item for item in hours if item['type'] == "Standard"), None)
        if store_hours:
            hours_str = f'Restaurant: {format_hours(store_hours)}'

        # for the drive thru hours, find the dict with type="Drivethru"
        drive_thru_hours = next(
            (item for item in hours if item['type'] == "Drivethru"), None)
        if drive_thru_hours:
            hours_str += '. ' if len(hours_str) > 0 else ''
            hours_str += f'Drive Thru: {format_hours(drive_thru_hours)}'

        # for the delivery hours, find the dict with type="Delivery"
        delivery_hours = next(
            (item for item in hours if item['type'] == "Delivery"), None)
        if delivery_hours:
            hours_str += '. ' if len(hours_str) > 0 else ''
            hours_str += f'Delivery: {format_hours(delivery_hours)}'

    if not hours_str:
        hours_str = '<MISSING>'

    return hours_str


def fetch_data():
    locs = []
    url = 'https://www.kfc.co.uk/cms/api/data/restaurants_all'
    r = session.get(url, headers=headers)

    data = r.json()
    for item in data:
        name = item['name']
        website = 'kfc.co.uk'
        typ = '<MISSING>'
        store = item['storeid']
        hours = ''
        country = 'GB'
        street = item['street'].replace('\n', ' ')
        city = item['city']
        state = '<MISSING>'
        zc = item['postalcode']
        lat = item['geolocation']['latitude']
        lng = item['geolocation']['longitude']
        hours = get_hours(item['hours'], item['status'])
        page_url = f'https://{website}{item["link"]}' if item["link"] else '<MISSING>'
        phone = '<MISSING>'

        yield [website, page_url, name, street, city, state, zc, country, store, phone, typ, lat, lng, hours]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
