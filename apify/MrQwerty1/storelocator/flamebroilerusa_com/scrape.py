import csv
from sgrequests import SgRequests


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
    url = 'https://flamebroilerusa.com/'
    api_url = 'https://locatorfbusa.gigasavvy.net//api/locations?limit=5000&radius=50000&search=75022'

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()['data']

    for j in js:
        locator_domain = url
        page_url = j.get('url')
        location_name = j.get('name').strip()
        street_address = f"{j.get('address')} {j.get('address_2') or ''}".strip() or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('state') or '<MISSING>'
        postal = j.get('zip') or '<MISSING>'
        country_code = 'US'
        store_number = j.get('store_id') or '<MISSING>'
        phone = j.get('phone') or '<MISSING>'
        latitude = j.get('lat') or '<MISSING>'
        longitude = j.get('lon') or '<MISSING>'
        location_type = '<MISSING>'

        _tmp = []
        hours = j.get('hours')

        for h in hours:
            day = h.keys()
            for d in day:
                start = h[d].get('open')[:-3]
                close = h[d].get('close')[:-3]
                _tmp.append(f'{d.capitalize()}: {start} - {close}')

        hours_of_operation = ';'.join(_tmp) or '<MISSING>'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
