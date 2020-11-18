import csv

from sgrequests import SgRequests
from lxml import html


def write_output(data):
    with open('data.csv', mode='w', encoding='utf8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        for row in data:
            writer.writerow(row)


def generate_ids():
    session = SgRequests()
    r = session.get('https://www.quicklane.com/en-ca/service-centre')
    tree = html.fromstring(r.text)
    out = []
    ids = tree.xpath("//h5/a[@class='store-url']/@href")
    for i in ids:
        out.append(i.split('/')[-1])
    return out


def fetch_data():
    out = []
    url = 'https://www.quicklane.com/en-ca/service-centre'

    session = SgRequests()
    headers = {'Origin': 'https://www.quicklane.com'}
    ids = generate_ids()

    for i in ids:
        r = session.get(f'https://www.quicklane.com/en-ca/stores.dealer.{i}.data', headers=headers)
        js = r.json()['qlDealer']
        s = js['seo']['quickLaneInfo'] or {}
        j = js['dealer']
        locator_domain = url
        street_address = j.get('streetAddress') or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        if city.endswith(','):
            city = city[:-1]
        location_name = j.get('dealerName') or '<MISSING>'
        state = j.get('state') or '<MISSING>'
        postal = j.get('zip') or '<MISSING>'
        country_code = j.get('country') or 'CA'
        store_number = i
        page_url = f'https://www.quicklane.com/en-ca/oil-change-tire-auto-repair-store/' \
                   f'{state}/{city}/{postal}/-/{i}' or '<MISSING> '

        phone = j.get('phone') or '<MISSING>'
        latitude = j.get('latitude') or '<MISSING>'
        longitude = j.get('longitude') or '<MISSING>'
        location_type = '<MISSING>'

        _tmp = []
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        cnt = 1
        for d in days:
            key = f'hours{cnt}'
            val = s.get(key, '')
            if val:
                _tmp.append(f'{d} {val}')
            cnt += 1
        hours_of_operation = ';'.join(_tmp) or '<MISSING>'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
