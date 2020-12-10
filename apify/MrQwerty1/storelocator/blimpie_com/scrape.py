import csv
import json

from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open('data.csv', mode='w', encoding='utf8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []
    url = 'https://www.blimpie.com/stores/'

    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.content)
    lines = ''.join(tree.xpath("//script[contains(text(), 'StoreId')]/text()"))

    for line in lines.split('\n'):
        # skip non json objects
        if line.find('Locator.stores') == -1:
            continue

        j = json.loads(line.split('=')[-1].strip())

        # status name - closed or coming soon
        if j.get('StatusName'):
            continue

        locator_domain = 'https://www.blimpie.com/'
        page_url = "https://www.blimpie.com/locator/"
        location_name = f"Blimpie Restaurant #{j.get('StoreId')}"
        street_address = j.get('Address') or '<MISSING>'
        if street_address.strip().endswith(','):
            street_address = street_address.strip()[:-1]
        city = j.get('City') or '<MISSING>'
        state = j.get('State') or '<MISSING>'
        postal = j.get('Zip') or '<MISSING>'
        country_code = j.get('CountryCode') or '<MISSING>'
        store_number = j.get('StoreId')
        phone = j.get('Phone') or '<MISSING>'
        latitude = j.get('Latitude') or '<MISSING>'
        longitude = j.get('Longitude') or '<MISSING>'
        location_type = '<MISSING>'
        hours_of_operation = '<MISSING>'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
