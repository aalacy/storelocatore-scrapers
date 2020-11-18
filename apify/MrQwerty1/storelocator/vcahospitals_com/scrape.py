import csv
import html
import json

from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html as lxml_html
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
    r = session.get('https://vcahospitals.com/find-a-hospital/location-directory')
    tree = lxml_html.fromstring(r.text)
    return tree.xpath("//div[@class='hospital']//h3/a/@href")


def get_exception(tree, page_url):
    locator_domain = 'http://vcahospitals.com/find-a-hospital/location-directory'
    location_name = html.unescape(''.join(tree.xpath("//div[@class='sh-contact-map__hospital']/text()")).strip())
    street_address = tree.xpath("//div[@class='sh-contact-map__txt-indent' and .//a]/p/text()")[0].strip()
    line = ''.join(tree.xpath("//div[@class='sh-contact-map__txt-indent' and .//a]/p[2]/text()")).strip()
    city = line.split(',')[0].strip()
    line = line.replace(f'{city},', '').strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = 'US'
    _tmp = ''.join(tree.xpath("//script[contains(text(), 'VCA.HospitalId')]/text()")).strip()
    store_number = _tmp.split('\n')[-1].split('"')[-2]
    phone = ''.join(tree.xpath("//div[@class='sh-contact-map__txt-indent']//a[contains(@href,'tel:')]/text()")).strip()
    if phone.find(',') != -1:
        phone = phone.split(',')[0]
    location_type = '<MISSING>'
    latitude = '<MISSING>'
    longitude = '<MISSING>'
    hours = ''.join(tree.xpath("//div[@class='sh-contact-map__txt-indent']/ul//text()")).strip()
    hours_of_operation = ';'.join([h.strip() for h in hours.split('\r\n')])

    row = [locator_domain, page_url, location_name, street_address, city, state, postal,
           country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
    return row


def get_data(url):
    session = SgRequests()
    locator_domain = 'http://vcahospitals.com/find-a-hospital/location-directory'
    page_url = f'http://vcahospitals.com{url}'
    r = session.get(page_url)
    tree = lxml_html.fromstring(r.text)

    # if the page doesn't contain JSON var, the page has another structure
    # e.g. https://vcahospitals.com/advanced-veterinary-care-center-ca
    try:
        j = json.loads(''.join(tree.xpath("//script[@type='application/ld+json']/text()")))
    except:
        # to avoid error because of bad / non-exists page
        # e.g. https://vcahospitals.com/california-veterinary-specialists-murrieta-sh-new
        try:
            row = get_exception(tree, page_url)
        except:
            row = None
        return row

    a = j.get('address', {})
    street_address = a.get('streetAddress') or '<MISSING>'
    city = a.get('addressLocality') or '<MISSING>'
    location_name = html.unescape(j.get('name')) or '<MISSING>'
    state = a.get('addressRegion') or '<MISSING>'
    postal = a.get('postalCode') or '<MISSING>'
    country_code = 'US'
    _tmp = ''.join(tree.xpath("//script[contains(text(), 'VCA.HospitalId')]/text()")).strip()
    store_number = _tmp.split('\n')[-1].split('"')[-2]
    phone = j.get('telephone') or '<MISSING>'
    g = j.get('geo', {})
    latitude = g.get('latitude') or '<MISSING>'
    longitude = g.get('longitude') or '<MISSING>'
    location_type = '<MISSING>'

    hours = tree.xpath("//div[@class='content']/div[contains(@class,'hours')]/ul/li[not(@class)]")
    _tmp = []
    for h in hours:
        day = ''.join(h.xpath("./p[@class='days']/text()")).strip()
        time = ''.join(h.xpath("./p[not(@class)]/text()")).strip()
        line = f'{day} {time}'
        _tmp.append(line)

    hours_of_operation = ';'.join(_tmp) or '<MISSING>'

    row = [locator_domain, page_url, location_name, street_address, city, state, postal,
           country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
    return row


def fetch_data():
    out = []
    s = set()
    threads = []
    urls = get_urls()

    with ThreadPoolExecutor(max_workers=20) as executor:
        for url in urls:
            threads.append(executor.submit(get_data, url))

    for task in as_completed(threads):
        row = task.result()
        if row:
            # to avoid duplicate; by store_number
            _id = row[-6]
            if _id not in s:
                s.add(_id)
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
