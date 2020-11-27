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
    s = set()
    url = 'https://impark.com/'
    api_url = 'https://www.discountcar.com/WebAPI2/api/v2/Location/GetAllLocations'

    session = SgRequests()
    data = {"latitude": 55.1810118, "longitude": -118.7940446, "radius": 5000}
    r = session.post(api_url, data=data)
    js = r.json()['body']

    for j in js:
        locator_domain = url
        location_name = j.get('name')
        street_address = j.get('address') or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('province') or '<MISSING>'
        postal = j.get('postalZipCode') or '<MISSING>'
        country_code = j.get('country') or '<MISSING>'
        if country_code == 'Canada':
            country_code = 'CA'
        else:
            country_code = 'US'

        store_number = j.get('locationID') or '<MISSING>'
        page_url = '<MISSING>'
        phone = j.get('phoneNumber') or '<MISSING>'
        if len(phone) < 10:
            phone = '<MISSING>'
        latitude = j.get('latitude') or '<MISSING>'
        longitude = j.get('longitude') or '<MISSING>'
        location_type = '<MISSING>'

        _tmp = []
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        hours = j.get('openHours') or {}
        for d in days:
            start = hours.get(f'{d[:3]}OpenTime')
            end = hours.get(f'{d[:3]}CloseTime')
            if start == '00:00':
                _tmp.append(f'{d.capitalize()}: Closed')
            else:
                _tmp.append(f'{d.capitalize()}: {start} - {end}')

        hours_of_operation = ';'.join(_tmp) or '<MISSING>'

        if hours_of_operation.count('Closed') == 7:
            continue

        line = (street_address, city, state)
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
