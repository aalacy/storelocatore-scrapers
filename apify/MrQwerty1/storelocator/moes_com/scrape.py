import csv
import json

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


def get_url_list():
    session = SgRequests()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'}
    r = session.get('https://www.moes.com/sitemap.xml', headers=headers)

    tree = html.fromstring(r.content)
    links = tree.xpath("//loc/text()")

    _tmp = set()
    for l in links:
        if l.split('/')[-1].isnumeric():
            _tmp.add(l)

    return _tmp


def fetch_data():
    out = []
    s = set()
    url = 'https://www.moes.com/find-a-moes'
    session = SgRequests()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'}
    urls = get_url_list()

    for u in urls:
        r = session.get(u, headers=headers)
        tree = html.fromstring(r.text)
        locator_domain = url
        page_url = u
        location_name = ''.join(tree.xpath("//h1/text()")).strip() or '<MISSING>'
        j = json.loads(''.join(tree.xpath("//script[contains(text(),'@context') and contains(text(), 'Rest')]/text()")))
        a = j.get('address')
        street_address = a.get('streetAddress') or '<MISSING>'
        city = a.get('addressLocality') or '<MISSING>'
        state = a.get('addressRegion') or '<MISSING>'
        postal = a.get('postalCode') or '<MISSING>'
        country_code = a.get('addressCountry') or '<MISSING>'
        store_number = u.split('/')[-1]
        if store_number not in s:
            s.add(store_number)
        else:
            continue
        phone = j.get('telephone') or '<MISSING>'
        latitude = ''.join(tree.xpath("//a/@data-lat")).strip() or '<MISSING>'
        longitude = ''.join(tree.xpath("//a/@data-long")).strip() or '<MISSING>'
        location_type = '<MISSING>'
        hours_of_operation = ';'.join(j.get('openingHours')) or '<MISSING>'

        if hours_of_operation.count('closed') == 7:
            hours_of_operation = 'closed'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

        print(row)
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
