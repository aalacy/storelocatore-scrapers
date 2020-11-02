import csv
from sgrequests import SgRequests
from lxml import etree
import json

base_url = 'https://www.bakerdist.com'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)

def parse_hours(hours_json):
    hours = []
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    for i in range(1, len(days) - 1):
        day = days[i - 1]
        for_day = hours_json[str(i)]
        if for_day['isOpen']:
            hours.append('{}: {}-{}'.format(day, for_day['open'], for_day['close']))
        else:
            hours.append('{}: closed'.format(day))
    return ', '.join(hours)

def fetch_data():
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"
    }
    response = session.get('https://www.bakerdist.com/store-locator/', headers=headers)
    parsed = etree.HTML(response.text)
    script = parsed.xpath('//script[@type="text/x-magento-init"][contains(text(), "storeLocator")]/text()')[0]
    stores = json.loads(script)["*"]["Magento_Ui/js/core/app"]["components"]["storeLocator"]["branches"]
    for store_number in stores:
        store = stores[store_number]
        if store['is_closed'] or store['is_distribution_center']:
            continue
        address = store['address']
        street = address['address_1']
        city = address['city']
        state = address['region_code']
        country = address['country']
        zipcode = address['postcode']
        name = store['branch_name']
        phone = store['phone']
        latitude = store['latitude']
        longitude = store['longitude']
        hours = parse_hours(store['formatted_hours'])
        location_type = '<MISSING>'
        page_url = '<MISSING>'
        yield [base_url, name, street, city, state, zipcode, country, store_number, phone, location_type, latitude, longitude, hours, page_url]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
