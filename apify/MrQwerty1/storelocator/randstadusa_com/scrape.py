import csv
import json

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


def get_urls(url):
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)
    return tree.xpath("//div[@class='title card-title']/a[contains(@href, '/locations/')]/@href")


def fetch_data():
    out = []
    url = 'https://www.randstadusa.com/locations/'

    session = SgRequests()
    urls = get_urls(url)

    for ur in urls:
        u = f'https://www.randstadusa.com{ur}'
        r = session.get(u)
        tree = html.fromstring(r.text)
        script = ''.join(tree.xpath("//script[contains(text(), 'var jsonData')]/text()"))
        _tmp = ''
        for l in script.split('\n'):
            if l.strip().startswith('var jsonData'):
                _tmp = l
                break
        jj = json.loads(_tmp.split("= '")[-1][:-3].strip())
        j = jj['features'][0]
        locator_domain = url
        page_url = u
        location_name = j.get('properties', {}).get('name') or '<MISSING>'
        street_address = f"{j.get('properties', {}).get('address1')} " \
                         f"{j.get('properties', {}).get('address2') or ''}".strip() or '<MISSING>'
        city = j.get('properties', {}).get('city') or '<MISSING>'
        state = j.get('properties', {}).get('state') or '<MISSING>'
        postal = j.get('properties', {}).get('postalcode') or '<MISSING>'
        country_code = 'US'
        store_number = u.split('_')[-1].split('/')[0]
        phone = tree.xpath("//div[@class='phone']//text()")[0].strip() or '<MISSING>'
        geo = j.get('geometry', {}).get('coordinates', [])
        latitude = geo[1] or '<MISSING>'
        longitude = geo[0] or '<MISSING>'
        # location_type = tree.xpath("//div[@class='specialties']//div[@class='name']/text()")[0].strip()
        location_type = '<MISSING>'
        hours = tree.xpath("//div[@id='collapse_hours']/div[@class='hours']")
        _tmp = []
        for h in hours:
            _tmp.append(' '.join(h.xpath('.//text()')))

        hours_of_operation = ';'.join(_tmp) or '<MISSING>'

        if hours_of_operation.count('closed') == 7:
            hours_of_operation = 'Closed'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

        out.append(row)
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
