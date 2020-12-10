import csv
import json
import urllib.parse
from lxml import etree

from sgrequests import SgRequests

DOMAIN = 'brueggers.com'


def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    
    start_url = 'https://locations.brueggers.com/us'
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    
    add_to_cities = []
    add_to_locations = []
    scraped_city_urls = []
    scraped_locations_urls = []
    allstates_urls = dom.xpath('//a[@class="Directory-listLink"]/@href')
    for state_url in allstates_urls:
        full_state_url = urllib.parse.urljoin(start_url, state_url)
        if len(state_url.split('/')) == 6:
            add_to_cities.append(state_url)
        
        state_response = session.get(full_state_url)
        state_dom = etree.HTML(state_response.text)

        add_cities_urls = state_dom.xpath('//a[@class="Directory-listLink"]/@href')
        for url in add_cities_urls:
            add_to_cities.append(url)
        
        all_locations = state_dom.xpath('//a[@data-ya-track="visit_page"]/@href')
        for url in all_locations:
            add_to_locations.append(urllib.parse.urljoin(start_url, url))
        
        allcities_urls = state_dom.xpath('//a[@class="Directory-listLink"]/@href')
        allcities_urls += add_to_cities
        for city_url in list(set(allcities_urls)):
            full_city_url = urllib.parse.urljoin(start_url, city_url)
            if len(full_city_url.split('/')) == 7:
                add_to_locations.append(full_city_url)
        
            city_response = session.get(full_city_url)
            scraped_city_urls.append(full_city_url)
            city_dom = etree.HTML(city_response.text)
            
            all_locations = city_dom.xpath('//a[@data-ya-track="visit_page"]/@href')
            all_locations += add_to_locations
            for location_url in list(set(all_locations)):
                full_location_url = urllib.parse.urljoin(start_url, location_url)
                if full_location_url in scraped_locations_urls:
                    continue
                location_response = session.get(full_location_url)
                scraped_locations_urls.append(full_location_url)
                location_dom = etree.HTML(location_response.text)
                store_url = full_location_url
                location_name = location_dom.xpath('//h1[@id="location-name"]/text()')[0]
                location_name = location_name if location_name else '<MISSING>'
                street_address = location_dom.xpath('//span[@class="c-address-street-1"]/text()')[0]
                street_address_2 = location_dom.xpath('//span[@class="c-address-street-2"]/text()')
                if street_address_2:
                    street_address += ' ' + street_address_2[0]
                street_address = street_address if street_address else '<MISSING>'
                city = location_dom.xpath('//span[@class="c-address-city"]/text()')[0]
                city = city if city else '<MISSING>'
                state = location_dom.xpath('//span[@itemprop="addressRegion"]/text()')[0]
                state = state if state else '<MISSING>'
                zip_code = location_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
                zip_code = zip_code if zip_code else '<MISSING>'
                
                country_code = full_state_url.split('/')[3]
                country_code = country_code.upper() if country_code else '<MISSING>'
                store_number = location_dom.xpath('//img[@itemprop="image"]/@id')[0]
                phone = location_dom.xpath('//a[@data-ya-track="phone"]/text()')[0]
                phone = phone if phone else '<MISSING>'
                location_type = '<MISSING>'
                latitude = location_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
                latitude = latitude if latitude else '<MISSING>'
                longitude = location_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
                longitude = longitude if longitude else '<MISSING>'
                
                hours_of_operation = json.loads(location_dom.xpath('//div/@data-days')[0])
                hours_list = []
                for elem in hours_of_operation:
                    if elem['intervals']:
                        day = elem['day']
                        start = elem['intervals'][0]['start'] / 100.0
                        end = elem['intervals'][0]['end'] / 100.0
                        day_hours = '{} {} AM - {} PM'.format(day, str(start), str(end))
                        hours_list.append(day_hours)
                hours_of_operation = ', '.join(hours_list) if hours_list else '<MISSING>'

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
