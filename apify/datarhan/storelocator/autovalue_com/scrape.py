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

    DOMAIN = 'autovalue.com'
    
    all_codes = []
    us_zips = sgzip.for_radius(radius=50, country_code=SearchableCountries.USA)
    for zip_code in us_zips:
        all_codes.append(zip_code)
    ca_zips = sgzip.for_radius(radius=50, country_code=SearchableCountries.CANADA)
    for zip_code in ca_zips:
        all_codes.append(zip_code)

    start_url = 'https://hosted.where2getit.com/autotalk/rest/locatorsearch?lang=en_US'
    for code in all_codes:
        body = '{"request":{"appkey":"F8FB03E8-C24B-11DD-AE46-C45F0AC4B31A","formdata":{"geoip":false,"dataview":"store_default","limit":5000,"geolocs":{"geoloc":[{"addressline":"' + code + '","country":"","latitude":"","longitude":""}]},"searchradius":"18|25|50|100|250","where":{"or":{"location_type":{"in":""}}},"false":"0"}}}'
        response = session.post(start_url, data=body)
        data = json.loads(response.text)
        if not data['response'].get('collection'):
            continue
        all_poi = data['response']['collection']
        for poi in all_poi:
            location_name = poi['servicing_location_name']
            location_name = location_name if location_name else '<MISSING>'
            street_address = poi['address1']
            if poi['address2']:
                street_address += ' ' + poi['address2']
            street_address = street_address if street_address else '<MISSING>'
            city = poi['city']
            city = city if city else '<MISSING>'
            state = poi['state']
            if not state:
                state = poi['province']
            state = state if state else '<MISSING>'
            zip_code = poi['postalcode']
            zip_code = zip_code if zip_code else '<MISSING>'
            country_code = poi['country']
            country_code = country_code if country_code else '<MISSING>'
            store_number = poi['servicing_location_id']
            store_number = store_number if store_number else '<MISSING>'
            store_url = '<MISSING>'
            if store_number != '<MISSING>':
                store_url = 'https://locations.autovalue.com/{}/{}/{}/'.format(state, city, store_number)
            phone = poi['phone']
            phone = phone if phone else '<MISSING>'
            location_type = poi['location_type']
            location_type = location_type if location_type else '<MISSING>'
            latitude = poi['latitude']
            latitude = latitude if latitude else '<MISSING>'
            longitude = poi['longitude']
            longitude = longitude if longitude else '<MISSING>'
            hours_of_operation = []
            days_keys = ['sunday', 'thursday', 'wednesday', 'tuesday', 'friday', 'monday', 'saturday']
            for elem in days_keys:
                hours_of_operation.append('{} - {}'.format(elem, poi[elem]))
            hours_of_operation = ', '.join(hours_of_operation) if hours_of_operation else '<MISSING>'
            
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
