import csv
import json
import usaddress
from lxml import etree

from sgrequests import SgRequests


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
    gathered_ids = []
    hdr = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6',
        'Connection': 'keep-alive',
        'Host': 'platoscloset.com',
        'Origin': 'http://platoscloset.com',
        'Referer': 'http://platoscloset.com/locations/list/WA',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    session = SgRequests()
    response = session.get('http://platoscloset.com/locations')
    dom = etree.HTML(response.text)
    all_states_urls = []
    for elem in dom.xpath('//div[@class="location-maps"]//a'):
        all_states_urls.append(elem.attrib['xlink:href'])
    
    for url in all_states_urls:
        state_url = 'http://platoscloset.com{}'.format(url)
        state_response = session.get(state_url)
        state_dom = etree.HTML(state_response.text)
        locations = state_dom.xpath('//div[@class="location-info-card"]')
        for location_dom in locations:
            location_name = location_dom.xpath('.//a[@class="location-name"]/text()')[0]
            if 'Coming Soon' in location_name:
                continue
            location_adr = location_dom.xpath('.//div[@class="location-address"]//text()')
            location_adr = [elem.strip() for elem in location_adr if elem.strip()]
            street_address = location_adr
            location_adr = usaddress.tag(', '.join(location_adr))
            location_adr = json.loads(json.dumps(location_adr))[0] 
            store_number = location_dom.xpath('.//a/@data-storenum')[0]
            phone = location_dom.xpath('.//a[@class="ga-link-phone"]/text()')
            phone = phone[0] if phone else '<MISSING>'
            location_type = location_dom.xpath('.//a[@class="location-name"]/text()')[0]
            hours_of_operation_raw = location_dom.xpath('//div[@class="hours-table"]//tbody/tr')
            hours_of_operation = []
            for hours_dom in hours_of_operation_raw:
                day = hours_dom.xpath('.//td[@class="day-col"]/text()')[0]
                time = hours_dom.xpath('.//td[@class="hours-col"]/text()')[0]
                hours_of_operation.append(', '.join([day, time]))
            zip_code = location_adr.get('ZipCode')
            zip_code = zip_code if zip_code else '<MISSING>'
            name = location_adr.get('PlaceName')
            name = name if name else '<MISSING>'
            state = location_adr.get('StateName')
            state = state if state else '<MISSING>'
            country_code = 'US'
            if '#ca' in url:
                country_code = 'CA'
                state = state.split()[0]
                zip_code = street_address[-1].split(state)[-1]
            
            item = [
                "platoscloset.com",
                state_url,
                location_name,
                street_address[0],
                name,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                "<MISSING>",
                "<MISSING>",
                '; '.join(hours_of_operation)
            ]
            if street_address not in gathered_ids:
                gathered_ids.append(street_address)
                items.append(item)
            
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
