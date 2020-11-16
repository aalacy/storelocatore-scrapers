import csv
import json
from lxml import etree
from sgselenium import SgFirefox

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

    DOMAIN = 'totalwine.com'

    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]

    start_url = 'https://www.totalwine.com/store-finder/browse/'
    for state in states:
        with SgFirefox() as driver:
            driver.get(start_url + state)
            dom = etree.HTML(driver.page_source)    

        all_poi = dom.xpath('//script[@data-react-helmet="true"]/text()')
        if not all_poi:
            continue
        if 'itemListElement' not in all_poi[0]:
            continue
        all_poi_data = json.loads(all_poi[0])
        for poi_data in all_poi_data['itemListElement']:
            poi_data = poi_data['item']
            store_url = poi_data['url']
            location_name = poi_data['name']
            location_name = location_name if location_name else '<MISSING>'
            street_address = poi_data['address']['streetAddress']
            street_address = street_address if street_address else '<MISSING>'
            city = poi_data['address']['addressLocality']
            city = city if city else '<MISSING>'
            state = poi_data['address']['addressRegion']
            state = state if state else '<MISSING>'
            zip_code = poi_data['address']['postalCode']
            zip_code = zip_code if zip_code else '<MISSING>'
            country_code = '<MISSING>'
            country_code = country_code if country_code else '<MISSING>'
            store_number = store_url.split('/')[-1]
            phone = poi_data['telephone']
            phone = phone if phone else '<MISSING>'
            location_type = poi_data['@type']
            location_type = location_type if location_type else '<MISSING>'
            latitude = poi_data['geo']['latitude']
            latitude = latitude if latitude else '<MISSING>'
            longitude = poi_data['geo']['longitude']
            longitude = longitude if longitude else '<MISSING>'
            hours_of_operation = '<INACCESSIBLE>'

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

            items.append(item)
    
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
