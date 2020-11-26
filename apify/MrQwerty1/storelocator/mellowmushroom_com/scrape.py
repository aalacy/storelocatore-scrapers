import csv
import html as h

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


def fetch_data():
    out = []
    url = 'https://mellowmushroom.com/'
    api_url = 'https://mellowmushroom.com/wp-admin/admin-ajax.php?action=store_search&autoload=1'

    session = SgRequests()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'}
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        locator_domain = url
        page_url = j.get('permalink') or '<MISSING>'
        part_name = h.unescape(j.get('store'))
        if part_name.lower().find('mellow mushroom') != -1:
            location_name = part_name
        else:
            location_name = f'Mellow Mushroom - {part_name}'
        street_address = f"{j.get('address')} {j.get('address2') or ''}".strip() or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('state') or '<MISSING>'
        postal = j.get('zip') or '<MISSING>'
        country_code = j.get('country') or '<MISSING>'
        store_number = j.get('id') or '<MISSING>'
        phone = j.get('phone') or '<MISSING>'
        latitude = j.get('lat') or '<MISSING>'
        longitude = j.get('lng') or '<MISSING>'
        location_type = '<MISSING>'

        lines = j.get('hours')
        if lines:
            tree = html.fromstring(lines)
            tr = tree.xpath("//tr")
            _tmp = []
            for t in tr:
                d = ''.join(t.xpath('./td[1]/text()')).strip()
                time = ''.join(t.xpath('.//time/text()')).strip()
                _tmp.append(f'{d} {time}')

            hours_of_operation = ';'.join(_tmp)
        else:
            hours_of_operation = 'Coming Soon'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
