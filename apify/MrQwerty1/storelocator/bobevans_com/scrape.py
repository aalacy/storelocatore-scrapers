import csv

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'}
    r = session.get('https://www.bobevans.com/sitemap.xml', headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//loc[contains(text(), '/locations/')]/text()")


def get_data(page_url):
    session = SgRequests()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'}
    slug = page_url.split('/')[-1]
    r = session.get(f'https://www.bobevans.com/api/location/details/{slug}', headers=headers)
    j = r.json()
    locator_domain = 'https://bobevans.com/'
    location_name = j.get('name') or '<MISSING>'
    street_address = j.get('streetAddress') or '<MISSING>'
    city = j.get('city') or '<MISSING>'
    state = j.get('state') or '<MISSING>'
    postal = j.get('zip') or '<MISSING>'
    country_code = 'US'
    store_number = j.get('storeNumber') or '<MISSING>'
    phone = j.get('telephone') or '<MISSING>'
    location_type = '<MISSING>'
    latitude = j.get('latitude') or '<MISSING>'
    longitude = j.get('longitude') or '<MISSING>'

    _tmp = []
    hours = j.get('weeklyBusinessHours', []) or []
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    for h in hours:
        day = days[h.get('day')]
        start_line = h.get('startUtc').split('T')[1]
        start = (datetime.strptime(start_line, '%H:%M:%SZ') - timedelta(hours=5)).strftime('%H:%M')
        end_line = h.get('endUtc').split('T')[1]
        end = (datetime.strptime(end_line, '%H:%M:%SZ') - timedelta(hours=5)).strftime('%H:%M')
        _tmp.append(f'{day} {start} - {end}')

    hours_of_operation = ';'.join(_tmp) or '<MISSING>'

    row = [locator_domain, page_url, location_name, street_address, city, state, postal,
           country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
    return row


def fetch_data():
    out = []
    threads = []
    urls = get_urls()

    with ThreadPoolExecutor(max_workers=5) as executor:
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
