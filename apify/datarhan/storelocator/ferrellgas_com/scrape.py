import re
import csv
import json
import urllib.parse
from lxml import etree

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

    DOMAIN = 'ferrellgas.com'

    start_url = 'https://www.ferrellgas.com/locations/all-locations/'
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_poi_urls = dom.xpath('//div[@class="city-card"]//h3/a/@href')
    for url in all_poi_urls:
        full_poi_url = urllib.parse.urljoin(start_url, url)
        poi_response = session.get(full_poi_url)
        poi_dom = etree.HTML(poi_response.text)

        store_url = full_poi_url
        location_name = poi_dom.xpath('//h1[@itemprop="name"]/text()')[0]
        location_name = location_name if location_name else '<MISSING>'
        street_address = poi_dom.xpath('//div[@itemprop="streetAddress"]/text()')[0]
        street_address = street_address if street_address else '<MISSING>'
        city = poi_dom.xpath('//span[@itemprop="addressLocality"]/text()')[0]
        city = city if city else '<MISSING>'
        state = poi_dom.xpath('//span[@itemprop="addressRegion"]/text()')[0]
        state = state if state else '<MISSING>'
        zip_code = poi_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = ''
        country_code = country_code if country_code else '<MISSING>'
        store_number = full_poi_url.split('/')[-1]
        store_number = store_number if store_number else '<MISSING>'
        phone = poi_dom.xpath('//a[@itemprop="telephone"]/text()')[0]
        phone = phone if phone else '<MISSING>'
        location_type = ''
        location_type = location_type if location_type else '<MISSING>'
        geo_data = poi_dom.xpath('//div[@class="location-detail__static-map"]//img/@src')
        latitude = '<MISSING>'
        longitude = '<MISSING>'
        if geo_data:
            geo_data = geo_data[0]
            geo_data = re.findall('red\%7C(.+)&key', geo_data)[0]
            latitude = geo_data.split(',')[0]
            longitude = geo_data.split(',')[-1]
        hours_of_operation = poi_dom.xpath('//h3[contains(text(), "Office Hours")]/following-sibling::ul[1]/li[@class="hours-list__item"]/text()')[1:]
        hours_of_operation = ', '.join([elem.strip() for elem in hours_of_operation])
        hours_of_operation = hours_of_operation if hours_of_operation else '<MISSING>'

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

        if street_address not in scraped_items:
            scraped_items.append(street_address)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
