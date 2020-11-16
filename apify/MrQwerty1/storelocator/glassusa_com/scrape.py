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


def get_states(url):
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)
    return tree.xpath("//div[@class='state-listing']//a/@href")


def generate_pin_dict(text):
    d = dict()
    for t in text.split('\n'):
        if t.find('branch') != -1:
            line = t.strip()[:-1].replace(':', '":').replace(',', ',"').replace('{', '{"')
            js = eval(f'{line.split("pop")[0][:-2]}}}')
            _id = js.get('branch')
            lat = js.get('latitude')
            lon = js.get('longitude')
            d[_id] = {'lat': lat, 'lon': lon}
        if t.find('];') != -1:
            break
    return d


def fetch_data():
    out = []
    session = SgRequests()
    url = 'https://www.glassusa.com/locations/'
    states = get_states(url)

    for s in states:
        r = session.get(f'https://www.glassusa.com{s}')
        tree = html.fromstring(r.text)
        locator_domain = url
        items = tree.xpath("//li[@class='group-container']")
        text = ''.join(tree.xpath("//script[contains(text(),'mapMarker ')]/text()"))
        _tmp = generate_pin_dict(text)
        for item in items:
            store_number = ''.join(item.xpath("./@data-branch"))
            page_url = 'https://www.glassusa.com' + ''.join(item.xpath("./@onclick")).split("'")[1]
            street_address = item.xpath(".//span[@class='item-address']/span[not(@class)]/text()")[0].strip()
            line = item.xpath(".//span[@class='item-address']/span[not(@class)]/text()")[1].strip()
            city = line.split(',')[0].strip()
            state = line.split(',')[1].strip()[:2]
            postal = line[-5:]
            country_code = 'US'
            location_name = ''.join(item.xpath(".//span[@class='loc-name highlight']/text()")).strip()
            phone = ''.join(item.xpath(".//span[@class='item-phone']/span[@class='highlight']/text()")).strip()
            latitude = _tmp.get(store_number, {}).get('lat') or '<MISSING>'
            longitude = _tmp.get(store_number, {}).get('lon') or '<MISSING>'
            if latitude == '0' or longitude == '0':
                latitude, longitude = '<MISSING>', '<MISSING>'
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
