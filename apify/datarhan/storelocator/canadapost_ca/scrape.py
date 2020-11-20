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

    DOMAIN = 'canadapost.ca'

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
    }

    all_coordinates = []
    ca_coordinates = sgzip.coords_for_radius(radius=10, country_code=SearchableCountries.CANADA)
    for coord in ca_coordinates:
        all_coordinates.append(coord)

    start_url = 'https://www.canadapost.ca/cpotools/apps/fpo/personal/findPostOfficeList?lat={}&lng={}'

    for coord in all_coordinates:
        lat, lng = coord
        response = session.get(start_url.format(lat, lng), headers=headers)
        dom = etree.HTML(response.text)
        
        all_poi_urls = dom.xpath('//form[@id="fpoListResultForm"]//a/@href')
        for poi_url in all_poi_urls:
            store_url = urllib.parse.urljoin(start_url, poi_url)
            store_response = session.get(store_url)
            store_dom = etree.HTML(store_response.text)

            address_raw = store_dom.xpath('//address/p/text()')
            address_list = [elem.strip() for elem in address_raw if elem.strip()]
            location_name = address_list[0]
            location_name = location_name if location_name else '<MISSING>'
            street_address = address_list[1]
            street_address = street_address if street_address else '<MISSING>'
            city = address_list[-1].replace('\xa0', ', ')
            city = ' '.join(city.split(',')[0].split()[:-1]) if city else '<MISSING>'
            state = address_list[-1].replace('\xa0', ', ')
            state = state.split(',')[0].split()[-1] if state else '<MISSING>'
            zip_code = address_list[-1].replace('\xa0', ', ')
            zip_code = zip_code.split(',')[-1].strip() if zip_code else '<MISSING>'
            country_code = '<MISSING>'
            country_code = country_code if country_code else '<MISSING>'
            store_number = location_name.split('#')
            store_number = store_number[-1] if len(store_number) == 2 else '<MISSING>'
            phone = ''
            phone = phone if phone else '<MISSING>'
            location_type = store_dom.xpath('//form//h5/text()')
            location_type = location_type[0] if location_type else '<MISSING>'
            if location_type != 'Post Office':
                continue
            latitude = store_dom.xpath('//input[@name="fpoDetailForm:latitude"]/@value')
            latitude = latitude[0] if latitude else '<MISSING>'
            longitude = store_dom.xpath('//input[@name="fpoDetailForm:longitude"]/@value')
            longitude = longitude[0] if longitude else '<MISSING>'
            hours_of_operation = []
            hours_html = store_dom.xpath('//div[@id="hoursOperation"]//tr')
            for day_html in hours_html:
                day = day_html.xpath('.//text()')[0]
                hours = day_html.xpath('.//text()')[-1]
                hours_of_operation.append('{} {}'.format(day, hours))
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

            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)
        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
