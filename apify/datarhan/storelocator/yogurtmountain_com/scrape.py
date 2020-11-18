import csv
import json
import usaddress
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
        adr_list = ', '.join([elem.strip() for elem in adr_list]).split('(located')[0].strip()
        try:
            location_dict = json.loads(json.dumps(usaddress.tag(adr_list)))[0]
            street_address_list = []
            for key, value in location_dict.items():
                if key == 'PlaceName':
                    break
                street_address_list.append(value)   
            street_address = ' '.join(street_address_list)
            city = location_dict.get('PlaceName')
            state = location_dict.get('StateName')
            zip_code = location_dict.get('ZipCode')
        except:
            street_address = ', '.join(adr_list.split(',')[:-2])
            city = adr_list.split(',')[-2].strip()
            state = adr_list.split(',')[-1].split()[0].strip()
            zip_code = adr_list.split(',')[-1].split()[1].strip()
        
        if not street_address.split()[0].isnumeric():
            for i, elem in enumerate(street_address.split()):
                if elem.isnumeric():
                    index = i
                    break
            street_address = ' '.join(street_address.split()[index:])
        street_address = street_address if street_address else '<MISSING>'    
        city = city if city else '<MISSING>'
        state = state if state else '<MISSING>'
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = '<MISSING>'
        store_number = '<MISSING>'
        phone = location.xpath('.//p[@class="phone"]/text()')
        phone = phone[0] if phone else ''
        phone = phone if phone else '<MISSING>'
        location_type = '<MISSING>'
        latitude = '<MISSING>'
        longitude = '<MISSING>'
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
