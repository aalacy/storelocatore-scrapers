import csv
import sgzip

from concurrent import futures
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


def get_ids():
    ids = []
    coords = sgzip.coords_for_radius(radius=200, country_code=SearchableCountries.USA)
    for coord in coords:
        ids.append(coord)
    return ids


def get_data(coord):
    _tmp_out = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'}
    locator_domain = 'https://cartridgeworld.com'
    lat, lng = coord

    session = SgRequests()
    r = session.get(f'https://cartridgeworld.com/wp-admin/admin-ajax.php?action=store_search'
                    f'&lat={lat}&lng={lng}&max_results=50&search_radius=500', headers=headers)

    js = r.json()
    for j in js:
        page_url = j.get('permalink') or '<MISSING>'
        location_name = j.get('store') or '<MISSING>'
        street_address = f"{j.get('address')} {j.get('address2') or ''}".strip() or '<MISSING>'
        if street_address.find('Business') != -1:
            street_address = '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('state') or '<MISSING>'
        postal = j.get('zip') or '<MISSING>'
        if len(postal) == 4:
            postal = f'0{postal}'
        country = j.get('country')
        if country == 'United States':
            country_code = 'US'
        elif country == 'Canada':
            country_code = 'CA'
        else:
            country_code = '<MISSING>'

        phone = j.get('phone') or '<MISSING>'
        store_number = j.get('id') or '<MISSING>'
        location_type = '<MISSING>'
        latitude = j.get('lat') or '<MISSING>'
        longitude = j.get('lng') or '<MISSING>'

        _tmp = []
        source = j.get('hours') or '<html></html>'
        tree = html.fromstring(source)
        tr = tree.xpath("//tr")
        for t in tr:
            day = ''.join(t.xpath('./td[1]/text()')).strip()
            time = ''.join(t.xpath('./td[2]//text()')).strip()
            _tmp.append(f'{day}: {time}')

        hours_of_operation = ';'.join(_tmp) or '<MISSING>'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

        _tmp_out.append(row)

    return _tmp_out


def fetch_data():
    out = []
    s = set()
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
