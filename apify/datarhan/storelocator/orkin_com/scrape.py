import csv
from lxml import etree
import fake_useragent

from sgrequests import SgRequests

DOMAIN = 'orkin.com'


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
    items = []

    ua = fake_useragent.UserAgent()
    scraped_urls = []
    scraped_locations = []

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    
    session = SgRequests()
    response = session.get('https://www.orkin.com/locations', headers=headers)
    dom = etree.HTML(response.text)
    allstates_urls = dom.xpath('//section[@class="layer static-map"]//a')
    for state_url in allstates_urls:
        full_state_url = 'https://www.orkin.com' + state_url.get('xlink:href')
        if full_state_url in scraped_urls:
            continue
        headers = {'user-agent': ua.random}
        state_response = session.get(full_state_url.replace(' ', ''), headers=headers)
        scraped_urls.append(full_state_url)
        state_dom = etree.HTML(state_response.text)
        allcities_urls = state_dom.xpath('//h4[contains(text(), "Select a City to View Branch Locations")]/following-sibling::div[1]//a/@href')
        for city_url in allcities_urls:
            full_city_url = 'https://www.orkin.com' + city_url
            if full_city_url in scraped_urls:
                continue
            headers = {'user-agent': ua.random}
            city_response = session.get(full_city_url.replace(' ', ''), headers=headers)
            scraped_urls.append(full_city_url)
            city_dom = etree.HTML(city_response.text)
            all_stores_data = city_dom.xpath('//section[@class="branch-data"]')
            for store_data in all_stores_data:
                store_url = '<MISSING>'
                location_name = store_data.find('h2').text
                location_name = location_name if location_name else '<MISSING>'
                street_address = store_data.xpath('.//span[@itemprop="streetAddress"]/text()')[0]
                street_address = street_address if street_address else '<MISSING>'
                city = store_data.xpath('.//span[@itemprop="addressLocality"]/text()')[0]
                city = city if city else '<MISSING>'
                state = store_data.xpath('.//span[@itemprop="addressRegion"]/text()')[0]
                state = state if state else '<MISSING>'
                zip_code = '<MISSING>'
                zip_code = zip_code if zip_code else '<MISSING>'
                country_code = '<MISSING>'
                country_code = country_code if country_code else '<MISSING>'
                store_number = location_name.split('#')[-1]
                phone = store_data.xpath('.//span[@itemprop="telephone"]/text()')[0]
                phone = phone if phone else '<MISSING>'
                location_type = store_data.get('data-service-type')
                location_type = location_type if location_type else '<MISSING>'
                latitude = '<MISSING>'
                latitude = latitude if latitude else '<MISSING>'
                longitude = '<MISSING>'
                longitude = longitude if longitude else '<MISSING>'
                hours_of_operation = store_data.xpath('.//span[@itemprop="dayOfWeek"]/span/p/text()')[0]

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

                if location_name not in scraped_locations:
                    scraped_locations.append(location_name)
                    items.append(item)
            
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
