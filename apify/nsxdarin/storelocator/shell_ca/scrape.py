import csv
import json
from sgrequests import SgRequests

INACCESSIBLE = '<INACCESSIBLE>'
session = SgRequests()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
}

canada = {
    "country_code": "CA",
    'bbox_sw': [41.6691, -141.0055],
    'bbox_ne': [74.5559, -52.6166],
}


def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def get_location_data(location):

    if (location.get('country_code') == 'CA'):
        return [
            locator_domain,
            location.get('website_url'),
            location.get('name'),
            location.get('address'),
            location.get('city'),
            location.get('state'),
            location.get('postcode'),
            location.get('country_code'),
            location.get('id'),
            location.get('telephone'),
            location.get('type'),
            location.get('lat'),
            location.get('lng'),
            INACCESSIBLE
        ]


locator_domain = 'shell.ca'


def fetch_within_bounds(sw, ne):
    params = {
        'sw[]': sw,
        'ne[]': ne,
        'autoload': True,
        'travel_mode': 'driving',
        'avoid_tolls': False,
        'avoid_highways': False,
        'avoid_ferries': False,
        'corridor_radius': 5,
        'driving_distances': False,
        'format': 'json'
    }

    data = session.get(f'https://shellgsllocator.geoapp.me/api/v1/locations/within_bounds',
                       headers=headers, params=params).json()

    for item in data:
        bounds = item.get('bounds')
        if bounds:
            yield from fetch_within_bounds(bounds.get(
                'sw'), bounds.get('ne'))
        else:
            if item.get('country_code') == 'CA':
                yield [
                    locator_domain,
                    item.get('website_url'),
                    item.get('name'),
                    item.get('address'),
                    item.get('city'),
                    item.get('state'),
                    item.get('postcode'),
                    item.get('country_code'),
                    item.get('id'),
                    item.get('telephone'),
                    item.get('type'),
                    item.get('lat'),
                    item.get('lng'),
                    INACCESSIBLE
                ]


def scrape():
    data = fetch_within_bounds(canada['bbox_sw'], canada['bbox_ne'])
    write_output(data)


scrape()
