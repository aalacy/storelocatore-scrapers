import csv
from lxml import etree

from sgrequests import SgRequests

DOMAIN = 'yogurtmountain.com'


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
    
    session = SgRequests()
    response = session.get('http://yogurtmountain.com/locations/')
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//ol[@id="list-locations"]/li')[1:]
    for location in all_locations:
        store_url = '<MISSING>'
        location_name = location.xpath('.//h3/text()')[0]
        location_name = location_name if location_name else '<MISSING>'
        adr_list = location.xpath('.//div[@class="loca-address loca-text list-column"]/p[1]//text()')
        if not adr_list:
            continue
        adr_list = [elem.strip() for elem in adr_list]
        street_address = ' '.join(adr_list[:-1])
        street_address = street_address if street_address else '<MISSING>'
        city = adr_list[-1].split(',')[0]
        city = city if city else '<MISSING>'
        state = adr_list[-1].split(',')[0].split()[0]
        state = state if state else '<MISSING>'
        zip_code = adr_list[-1].split(',')[0].split()[-1]
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = '<MISSING>'
        country_code = country_code if country_code else '<MISSING>'
        store_number = '<MISSING>'
        phone = location.xpath('.//p[@class="phone"]/text()')
        phone = phone[0] if phone else ''
        phone = phone if phone else '<MISSING>'
        location_type = '<MISSING>'
        latitude = '<MISSING>'
        latitude = latitude if latitude else '<MISSING>'
        longitude = '<MISSING>'
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = location.xpath('.//div[@class="loca-hours loca-text list-column"]/p[2]//text()')
        hours_of_operation = ', '.join([elem.strip() for elem in hours_of_operation]) if hours_of_operation else '<MISSING>'

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
