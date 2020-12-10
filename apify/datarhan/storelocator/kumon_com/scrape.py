import csv
import json
import sgzip
import urllib.parse
from lxml import etree
from sgzip import SearchableCountries

from sgrequests import SgRequests


def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = 'kumon.com'

    hdr = {
        'authority': 'www.kumon.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6',
        'content-type': 'application/json; charset=UTF-8',
        'origin': 'https://www.kumon.com',
        'referer': 'https://www.kumon.com/locations',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    all_coordinates = []
    us_coordinates = sgzip.coords_for_radius(radius=50, country_code=SearchableCountries.USA)
    for coord in us_coordinates:
        all_coordinates.append(coord)
    ca_coordinates = sgzip.coords_for_radius(radius=50, country_code=SearchableCountries.CANADA)
    for coord in ca_coordinates:
        all_coordinates.append(coord)

    start_url = 'https://www.kumon.com/Services/KumonWebService.asmx/GetCenterListByRadius'

    for coord in all_coordinates:
        lat, lng = coord
        body = '{"latitude":%s,"longitude":%s,"radius":250,"distanceUnit":"mi"}' % (lat, lng)
        response = session.post(start_url, data=body, headers=hdr)
        data = json.loads(response.text)
        
        all_poi = data['d']
        for poi in all_poi:
            store_url = 'https://www.kumon.com/{}'.format(poi['EpageUrl'])
            location_name = poi['CenterName']
            location_name = location_name if location_name else '<MISSING>'
            street_address = poi['Address']
            if poi.get('Address2'):
                street_address += ', ' + poi['Address2']
            if poi.get('Address3'):
                street_address += ' ' + poi['Address3']
            street_address = street_address if street_address else '<MISSING>'
            city = poi['City']
            city = city if city else '<MISSING>'
            state = poi['StateCode']
            state = state if state else '<MISSING>'
            zip_code = poi['ZipCode']
            zip_code = zip_code if zip_code else '<MISSING>'
            country_code = poi['Country']
            country_code = country_code if country_code else '<MISSING>'
            store_number = poi['K2CenterID']
            store_number = store_number if store_number else '<MISSING>'
            phone = poi['Phone']
            phone = phone if phone else '<MISSING>'
            location_type = '<MISSING>'
            location_type = location_type if location_type else '<MISSING>'
            latitude = poi['Lat']
            latitude = latitude if latitude else '<MISSING>'
            longitude = poi['Lng']
            longitude = longitude if longitude else '<MISSING>'
            hours_of_operation = '<MISSING>'
            
            item = [
                DOMAIN,
                store_url,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation
            ]

            if location_name not in scraped_items:
                scraped_items.append(location_name)
                items.append(item)
        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
