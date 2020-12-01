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

    DOMAIN = 'jaguar.ca'

    start_url = 'https://www.jaguar.ca/en/retailer-locator/index.html?radius=100&postCode={}+1a1&filter=dealer'
    hdr = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'}

    all_codes = []
    ca_zips = sgzip.for_radius(radius=50, country_code=SearchableCountries.CANADA)
    for ca_code in ca_zips:
        all_codes.append(ca_code)

    for code in all_codes:
        response = session.get(start_url.format(code, headers=hdr))
        dom = etree.HTML(response.text)

        all_poi_html = dom.xpath('//div[@class="infoCardDealer infoCard"]')
        for poi_html in all_poi_html:
            store_url = poi_html.xpath('.//div[@class="dealerWebsiteDiv"]//a/@href')
            store_url = store_url[0] if store_url else '<MISSING>'
            location_name = poi_html.xpath('.//span[@class="dealerNameText fontBodyCopyLarge"]/text()')
            location_name = location_name[0] if location_name else '<MISSING>'
            street_address_raw = poi_html.xpath('.//span[@class="addressText"]/text()')[0]
            street_address = street_address_raw.split(',')[0]
            street_address = street_address if street_address else '<MISSING>'
            city = street_address_raw.split(',')[1].strip()
            city = city if city else '<MISSING>'
            state = street_address_raw.split(',')[2].strip()
            state = state if state else '<MISSING>'
            zip_code = street_address_raw.split(',')[3].strip()
            zip_code = zip_code if zip_code else '<MISSING>'
            country_code = ''
            country_code = country_code if country_code else '<MISSING>'
            store_number = poi_html.xpath('@data-ci-code')[0]
            store_number = store_number if store_number else '<MISSING>'
            phone = poi_html.xpath('.//a[@class="itemMobileInner"]/text()')
            phone = phone[0] if phone else '<MISSING>'
            location_type = ''
            location_type = location_type if location_type else '<MISSING>'
            latitude = poi_html.xpath('@data-lat')[0]
            latitude = latitude if latitude else '<MISSING>'
            longitude = poi_html.xpath('@data-lng')[0]
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

            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)
        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
