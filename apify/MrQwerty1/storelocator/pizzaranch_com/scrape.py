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
    urls = []
    session = SgRequests()
    for i in range(1, 5000):
        r = session.get(f'https://pizzaranch.com/all-locations/search-results/p{i}?state=*')
        tree = html.fromstring(r.text)
        links = tree.xpath("//location-info-panel")
        for l in links:
            lines = l.get(':location', '').split('\n')
            for line in lines:
                if line.find('url:') != -1:
                    u = line.split("'")[1]
                    urls.append(u)
        if len(links) < 12:
            break
    return urls


def get_data(url):
    locator_domain = 'https://pizzaranch.com'
    page_url = url

    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)

    location_name = ''.join(tree.xpath("//h1[@itemprop='name']//text()")).strip()
    street_address = ''.join(tree.xpath("//span[@itemprop='streetAddress']//text()")).strip()
    city = ''.join(tree.xpath("//span[@itemprop='addressLocality']//text()")).strip()
    state = ''.join(tree.xpath("//abbr[@itemprop='addressRegion']//text()")).strip()
    postal = ''.join(tree.xpath("//span[@itemprop='postalCode']//text()")).strip()
    country_code = 'US'
    store_number = '<MISSING>'
    phone = ''.join(tree.xpath("//span[@itemprop='telephone']//text()")).strip()
    location_type = '<MISSING>'
    latitude = tree.xpath("//meta[@itemprop='latitude']/@content")[0]
    longitude = tree.xpath("//meta[@itemprop='longitude']/@content")[0]

    _tmp = []

    hours = tree.xpath("//div[@class='location-info-right-wrapper']//table[@class='c-location-hours-details']"
                       "//tr[contains(@class, 'c-location-hours-details')]")
    for h in hours:
        day = ''.join(h.xpath("./td[@class='c-location-hours-details-row-day']/text()"))
        time = ' '.join(h.xpath(".//span[@class='c-location-hours-details-row-intervals-instance ']//text()"))
        if time:
            _tmp.append(f'{day} {time}')
        else:
            _tmp.append(f'{day} Closed')

    if _tmp:
        hours_of_operation = ';'.join(_tmp)

        if hours_of_operation.count('Closed') == 7:
            hours_of_operation = 'Closed'
    else:
        hours_of_operation = 'Coming Soon'

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
