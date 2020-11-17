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

    DOMAIN = 'midas.com'

    start_url = 'https://www.midas.com/partialglobalsearch/getstorelist?zipcode={}&language=en-us'
    hdr = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'}

    all_codes = []
    us_zips = sgzip.for_radius(radius=50, country_code=SearchableCountries.USA)
    for zip_code in us_zips:
        all_codes.append(zip_code)
    ca_zips = sgzip.for_radius(radius=50, country_code=SearchableCountries.CANADA)
    for zip_code in ca_zips:
        all_codes.append(zip_code)

    for code in all_codes:
        inccorect_request = False
        try:
            response = session.get(start_url.format(code), headers=hdr)
        except Exception as ex:
            inccorect_request = True
        if inccorect_request:
            continue

        data = json.loads(response.text)
        for poi in data:
            store_url = urllib.parse.urljoin(start_url, poi['ShopDetailsLink'])
            location_name = poi['Name']
            location_name = location_name if location_name else '<MISSING>'
            street_address = poi['Address']
            street_address = street_address if street_address else '<MISSING>'
            city = poi['City']
            city = city if city else '<MISSING>'
            state = poi['State']
            state = state if state else '<MISSING>'
            zip_code = poi['ZipCode']
            zip_code = zip_code if zip_code else '<MISSING>'
            country_code = poi['Country']
            country_code = country_code if country_code else '<MISSING>'
            store_number = poi['ShopNumber']
            store_number = store_number if store_number else '<MISSING>'
            phone = poi['PhoneNumber']
            phone = phone if phone else '<MISSING>'
            location_type = '<MISSING>'
            location_type = location_type if location_type else '<MISSING>'
            latitude = poi['Latitude']
            latitude = latitude if latitude else '<MISSING>'
            longitude = poi['Longitude']
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
