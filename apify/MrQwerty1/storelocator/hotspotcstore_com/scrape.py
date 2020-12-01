import csv
import re

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


def get_phone(text):
    regex = r'(\d{3}-\d{3}-\d{4}|\(\d{3}\) \d{3}-\d{4})'
    phone = re.findall(regex, text)
    if phone:
        return phone[0].strip()
    return '<MISSING>'


def fetch_data():
    out = []
    url = 'https://hotspotcstore.com'

    session = SgRequests()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    r = session.get('https://hotspotcstore.com/locations/', headers=headers)
    tree = html.fromstring(r.text)
    shops = tree.xpath("//p[./strong or ./b]")
    for shop in shops:
        locator_domain = url
        location_name = shop.xpath('./*/text()')[0] or '<MISSING>'
        lines = shop.xpath("./text()")
        lines = list(filter(None, [l.strip() for l in lines]))
        street_address = lines[0] or '<MISSING>'
        postal = lines[1].split()[-1].strip()
        state = lines[1].split()[-2].split()[0].strip()
        city = lines[1].replace(postal, '').replace(state, '').replace(',', '').strip()
        country_code = 'US'
        store_number = location_name.split()[-1].strip()
        phone = get_phone(''.join(lines))
        page_url = 'https://hotspotcstore.com/locations/'
        latitude = '<MISSING>'
        longitude = '<MISSING>'
        location_type = '<MISSING>'
        hours_of_operation = '<MISSING>'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
