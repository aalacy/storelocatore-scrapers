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
    url = 'https://www.togos.com/locations/'
    api_url = 'https://www.togos.com/locations/getLocationJson'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'}
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()['markers']

    for j in js:
        locator_domain = url
        page_url = f"{url}{j.get('city_slug')}/{j.get('address_slug')}"
        location_name = f"{j.get('city')} {j.get('fields', {}).get('cross_streets')}"
        street_address = j.get('address') or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('state') or '<MISSING>'
        postal = j.get('zipcode') or '<MISSING>'
        country_code = j['country']
        store_number = '<MISSING>'
        phone = j.get('phone') or '<MISSING>'
        latitude = j.get('lat') or '<MISSING>'
        longitude = j.get('lng') or '<MISSING>'
        location_type = '<MISSING>'

        _tmp = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = j.get('hours').split(';')
        for d, h in zip(days, hours):
            start = h.split(',')[1]
            start_time = f'{start[:2]}:{start[2:]}'
            close = h.split(',')[2]
            close_time = f'{close[:2]}:{close[2:]}'
            if start == '' or close == '':
                _tmp.append(f'{d} CLOSED')
            else:
                _tmp.append(f'{d} {start_time} - {close_time}')

        hours_of_operation = ';'.join(_tmp)

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
