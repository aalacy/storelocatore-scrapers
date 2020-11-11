import re
import csv
import json
import time

from sgrequests import SgRequests
from sgselenium import SgFirefox, SgSelenium


class SgSeleniumDelay(SgSelenium):
    '''
    Added delay to get token.
    Returns list of dictionaries
    '''

    def get_default_headers_for(driver, request_url: str) -> dict:
        driver.get(request_url)
        time.sleep(3)
        return driver.get_cookies()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    all_cookies = {}
    with SgFirefox() as driver:
        headers = SgSeleniumDelay.get_default_headers_for(driver, 'https://www.musicgoround.com/locations')
        for elem in headers:
            if elem['name'] == 'ordercloud.token':
                token = elem['value']
    
    hdr = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6',
        'Authorization': 'Bearer {}'.format(token),
        'Connection': 'keep-alive',
        'Host': 'api.ordercloud.io',
        'Origin': 'https://www.musicgoround.com',
        'Referer': 'https://www.musicgoround.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }

    items = []

    all_locations_url = 'https://api.ordercloud.io/v1/suppliers?pageSize=40&page=1&Active=true&sortBy=Name'
    session = SgRequests()
    response = session.get(all_locations_url, headers=hdr)
    data = json.loads(response.text)
    for location_data in data['Items']:
        location_details_url = 'https://api.ordercloud.io/v1/suppliers/{}/addresses/{}'.format(location_data['ID'], location_data['ID'])
        location_response = session.get(location_details_url, headers=hdr)
        location_full_data = json.loads(location_response.text)
        location_type = '{} Store'.format(location_full_data['CompanyName'])
        latitude = location_data['xp']['latitude']
        latitude = latitude if latitude != 0 else '<MISSING>'
        longitude = location_data['xp']['longitude']
        longitude = longitude if longitude != 0 else '<MISSING>'
        
        item = [
            'musicgoround.com',
            'https://www.musicgoround.com/locations/{}'.format(location_data['xp']['slug']),
            location_full_data['CompanyName'],
            location_full_data['Street1'],
            location_full_data['City'],
            location_full_data['State'],
            location_full_data['Zip'],
            location_full_data['Country'],
            location_full_data['ID'],
            location_full_data['Phone'].split('/')[0],
            location_type,
            latitude,
            longitude,
            location_full_data['xp']['hours']
        ]
        items.append(item)
        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
