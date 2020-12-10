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
    url = 'https://unitedrentals.com/'
    api_url = 'https://www.unitedrentals.com/api/v2/branches'

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()['data']

    s = set()
    for j in js:
        locator_domain = url
        page_url = f'https://www.unitedrentals.com{j.get("url")}'
        location_name = j.get('name').strip()
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip() or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('state') or '<MISSING>'
        postal = j.get('zip') or '<MISSING>'
        country_code = j.get('countryCode') or '<MISSING>'
        store_number = j.get('branchId') or '<MISSING>'
        phone = j.get('phone') or '<MISSING>'
        if phone == '00':
            phone = '<MISSING>'
        latitude = j.get('latitude') or '<MISSING>'
        longitude = j.get('longitude') or '<MISSING>'
        location_type = '<MISSING>'

        _tmp = []
        start = j.get('weekdayHours').get('open')
        close = j.get('weekdayHours').get('close')
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for d in days:
            if d.startswith('sat') or d.startswith('sun') or not start:
                _tmp.append(f'{d.capitalize()}: Closed')
            else:
                _tmp.append(f'{d.capitalize()}: {start} - {close}')

        hours_of_operation = ';'.join(_tmp)

        if hours_of_operation.count('Closed') == 7:
            continue

        line = (street_address, city, state, postal)
        if line in s:
            continue

        s.add(line)
        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
