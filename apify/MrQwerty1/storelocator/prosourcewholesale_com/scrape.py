import csv
import json

from concurrent import futures
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


def get_ids():
    ids = []
    session = SgRequests()
    r = session.get('https://www.prosourcewholesale.com/showrooms')
    tree = html.fromstring(r.text)
    lines = ''.join(tree.xpath("//script[contains(text(),'sitecoreShowrooms.push')]/text()")).split('\n')
    for l in lines:
        if l.find('sitecoreShowrooms.push') != -1:
            js = json.loads(l.split('push(')[1].split(');')[0])
            part = js['URL']
            ids.append(f'https://www.prosourcewholesale.com{part}')

    return ids


def get_data(_id):
    locator_domain = 'https://www.prosourcewholesale.com/'
    page_url = _id

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    j = json.loads(''.join(tree.xpath("//script[@type='application/ld+json']/text()")))

    location_name = j.get('name')
    a = j.get('address') or {}
    street_address = a.get('streetAddress') or '<MISSING>'
    city = a.get('addressLocality') or '<MISSING>'
    state = a.get('addressRegion') or '<MISSING>'
    postal = a.get('postalCode') or '<MISSING>'
    country_code = a.get('addressCountry') or '<MISSING>'
    if country_code == 'USA':
        country_code = 'US'
    else:
        country_code = 'CA'

    phone = j.get('telephone') or '<MISSING>'
    store_number = '<MISSING>'
    location_type = '<MISSING>'

    g = j.get('geo') or {}
    latitude = g.get('latitude') or '<MISSING>'
    longitude = g.get('longitude') or '<MISSING>'

    hours_of_operation = j.get('openingHours') or '<MISSING>'

    row = [locator_domain, page_url, location_name, street_address, city, state, postal,
           country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

    return row


def fetch_data():
    out = []
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
