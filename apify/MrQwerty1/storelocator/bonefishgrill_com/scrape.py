import csv
import json

from concurrent.futures import ThreadPoolExecutor, as_completed
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


def get_urls():
    session = SgRequests()
    r = session.get(f'https://www.bonefishgrill.com/locations/all')
    tree = html.fromstring(r.text)
    return tree.xpath("//li[@class='location-row']/a/@href")


def get_data(u):
    locator_domain = 'https://bonefishgrill.com/'
    url = f'https://bonefishgrill.com{u}'
    page_url = url

    # some of pages are broken
    # e. g. https://bonefishgrill.com/locations/fl/ft.-lauderdale
    if u.find('.') != -1:
        return

    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)

    text = ''.join(tree.xpath("//script[contains(text(), '{ initLocationDetail')]/text()"))
    line = ','.join(text.split(',')[1:]).split(');')[0].strip()
    j = json.loads(line)

    location_name = f"BONEFISH GRILL {j.get('Name')}"
    street_address = j.get('Address') or '<MISSING>'
    city = j.get('City') or '<MISSING>'
    state = j.get('State') or '<MISSING>'
    postal = j.get('Zip') or '<MISSING>'
    country_code = 'US'
    store_number = j.get('UnitId') or '<MISSING>'
    phone = j.get('Phone') or '<MISSING>'
    location_type = '<MISSING>'
    latitude = j.get('Latitude') or '<MISSING>'
    longitude = j.get('Longitude') or '<MISSING>'

    _tmp = []
    hours = j.get('StoreHours', []) or []

    for h in hours:
        day = h.get('Key')
        time = h.get('Value')
        if time:
            _tmp.append(f'{day} {time}')
        else:
            _tmp.append(f'{day} Closed')

    hours_of_operation = ';'.join(_tmp) or '<MISSING>'

    row = [locator_domain, page_url, location_name, street_address, city, state, postal,
           country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
    return row


def fetch_data():
    out = []
    threads = []
    urls = get_urls()
    with ThreadPoolExecutor(max_workers=10) as executor:
        for url in urls:
            threads.append(executor.submit(get_data, url))

    for task in as_completed(threads):
        row = task.result()
        if row:
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
