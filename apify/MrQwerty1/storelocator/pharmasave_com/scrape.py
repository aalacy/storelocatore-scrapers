import csv

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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'}
    r = session.get('https://pharmasave.com/store-sitemap.xml', headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//loc/text()")


def get_data(page_url):
    session = SgRequests()
    locator_domain = 'https://pharmasave.com/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'}

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    street_address = ''.join(tree.xpath("//div[@style='clear: both;']/text()")).strip() or '<MISSING>'
    line = tree.xpath("//div[./div[@style='clear: both;']]/text()")
    line = list(filter(None, [l.strip() for l in line]))
    if not line:
        return
    city = line[0] or '<MISSING>'
    location_name = ''.join(tree.xpath("//h1[@class='header-title__title']/text()")).strip()
    state = line[2] or '<MISSING>'
    postal = line[1] or '<MISSING>'
    country_code = 'CA'
    store_number = '<MISSING>'
    phone = line[3] or '<MISSING>'
    text = ''.join(tree.xpath("//script[contains(text(), 'startMap()')]/text()"))
    latitude = '<MISSING>'
    longitude = '<MISSING>'
    for t in text.split('\n'):
        if t.find('var lat') != -1:
            latitude = t.split('=')[1].strip()[:-1]
        if t.find('var lon') != -1:
            longitude = t.split('=')[1].strip()[:-1]

    location_type = '<MISSING>'

    _tmp = []
    li = tree.xpath("//ul[@class='store__single-hours'][1]/li")
    for l in li:
        _tmp.append(f"{' '.join(l.xpath('.//text()')).strip()}")

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
