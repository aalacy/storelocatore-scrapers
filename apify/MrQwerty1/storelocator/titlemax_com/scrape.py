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
    r = session.get('https://www.titlemax.com/stores.xml')
    tree = html.fromstring(r.content)
    return tree.xpath("//loc/text()")


def get_data(page_url):
    session = SgRequests()

    locator_domain = 'https://titlemax.com/'
    for i in range(5):
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        try:
            sect = tree.xpath("//section[@id='storeHeader']")[0]
            break
        except IndexError:
            pass
    else:
        return
    location_name = ''.join(sect.xpath(".//h1[@itemprop='name']/text()")).strip()
    street_address = ''.join(sect.xpath(".//div[@itemprop='streetAddress']/text()")).strip()
    city = ''.join(sect.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
    state = ''.join(sect.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
    postal = sect.xpath(".//div[@class='store-address-2']/text()")[-1].strip()
    country_code = 'US'
    store_number = '<MISSING>'
    phone = ''.join(sect.xpath(".//span[@itemprop='telephone']/text()")).strip()
    if page_url.find('pawns') != -1:
        location_type = 'Title Pawns'
    elif page_url.find('loans') != -1:
        location_type = 'Title Loans'
    elif page_url.find('appraiser') != -1:
        location_type = 'TitleMax Appraisals'
    else:
        location_type = 'Title Loans'

    line = ''.join(tree.xpath("//a[contains(@href, 'maps.google')]/@href"))
    if line:
        latitude = line.split('=')[-1].split(',')[0]
        longitude = line.split('=')[-1].split(',')[1]
    else:
        latitude = '<MISSING>'
        longitude = '<MISSING>'

    _tmp = []
    hours_keys = tree.xpath("//div[contains(@class, 'storeHours')]/strong/text()")
    hours_values = tree.xpath("//div[contains(@class, 'storeHours')]/text()")
    hours_values = list(filter(None, [h.strip() for h in hours_values]))
    for k, v in zip(hours_keys, hours_values):
        _tmp.append(f'{k.strip()} {v.strip()}')
    hours_of_operation = ';'.join(_tmp) or 'Temporarily closed'

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
