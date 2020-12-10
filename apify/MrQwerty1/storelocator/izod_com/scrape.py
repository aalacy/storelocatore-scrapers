import csv
import sgzip
import urllib.parse

from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
from sgrequests import SgRequests
from sgzip import SearchableCountries


def write_output(data):
    with open('data.csv', mode='w', encoding='utf8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        for row in data:
            writer.writerow(row)


def get_data(postal):
    _tmp_out = []
    session = SgRequests()
    locator_domain = 'https://izod.com/'
    page_url = f'https://secure.gotwww.com/gotlocations.com/vanheusendev/index.php?address={postal}'

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    script = ''.join(tree.xpath("//script[contains(text(),'L.marker')]/text()"))
    for line in script.split('\n'):
        if line.find('L.marker') == -1 or line.find('IZOD') == -1:
            continue
        root = html.fromstring(line.split("'")[1])
        a = ''.join(root.xpath("//a/@href")).split('=')[-1]
        street_address = urllib.parse.unquote(a.split(',')[0].replace('+', ' ').strip()) or '<MISSING>'
        city = a.split(',')[1].replace('+', ' ').strip() or '<MISSING>'
        state = a.split(',')[2].replace('+', ' ').strip() or '<MISSING>'
        postal = a.split(',')[3].replace('+', ' ').strip() or '<MISSING>'
        country_code = a.split(',')[4].replace('+', ' ').strip()
        location_name = '<MISSING>'
        store_number = '<MISSING>'
        phone = root.xpath("//div[@class='map_text']/text()")[-1].replace('Phone:', '').strip() or '<MISSING>'
        latitude = line.split('[')[1].split(',')[0] or '<MISSING>'
        longitude = line.split(']')[0].split(',')[-1] or '<MISSING>'
        location_type = '<MISSING>'
        hours_of_operation = '<MISSING>'
        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        _tmp_out.append(row)
    return _tmp_out


def fetch_data():
    out = []
    s = set()
    threads = []
    zips = sgzip.for_radius(radius=10, country_code=SearchableCountries.USA)

    with ThreadPoolExecutor(max_workers=20) as executor:
        for postal in zips:
            threads.append(executor.submit(get_data, postal))

    for task in as_completed(threads):
        _tmp = task.result()
        for t in _tmp:
            line = ';'.join(t[2:6])
            if line not in s:
                s.add(line)
                out.append(t)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
