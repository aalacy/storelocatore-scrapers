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
    r = session.get('https://www.eyemartexpress.com/sitemap')
    tree = html.fromstring(r.content)
    return tree.xpath("//loc[contains(text(), 'eyemartexpress.com/get-glasses/')]/text()")


def get_data(url):
    session = SgRequests()
    locator_domain = 'https://eyemartexpress.com/'
    page_url = url
    r = session.get(page_url)
    if url != r.url:
        return
    tree = html.fromstring(r.text)
    location_name = ''.join(tree.xpath("//h1/span/text()")).strip() or '<MISSING>'

    street_address = ''.join(tree.xpath("//div[@itemprop='address']/p[2]/text()")).strip() or '<MISSING>'
    a = ''.join(tree.xpath("//div[@itemprop='address']/p[3]/text()")).strip()
    if a:
        city = a.split(',')[0].strip()
        a = a.split(',')[1].strip()
        state = a[:2]
        postal = a.replace(state, '').strip()
    else:
        city = '<MISSING>'
        state = '<MISSING>'
        postal = '<MISSING>'
    country_code = 'US'
    store_number = url.split('/')[-1]
    phone = ''.join(tree.xpath("//p[@class='my-h-mobile']/a[contains(@href, 'tel:')]/text()")) or '<MISSING>'
    g = ''.join(tree.xpath("//a[contains(@href, '/maps/search/')]/@href")).split('&query=')[1].split('&')[0]
    latitude = g.split(',')[0]
    longitude = g.split(',')[1]
    location_type = '<MISSING>'

    hours = tree.xpath("//div[./p[contains(text(), 'Hours')]]/p[@class='m-0']/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ';'.join(hours) or '<MISSING>'

    row = [locator_domain, page_url, location_name, street_address, city, state, postal,
           country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
    return row


def fetch_data():
    out = []
    threads = []
    urls = get_urls()

    with ThreadPoolExecutor(max_workers=20) as executor:
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
