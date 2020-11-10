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
    url = 'https://locations.captainds.com/'

    session = SgRequests()

    for i in range(1, 10000):
        api_url = f'https://momentfeed-prod.apigee.net/api/llp.json?auth_token=AJXCZOENNNXKHAKZ&pageSize=100&page={i}'
        r = session.get(api_url)
        js = r.json()

        for j in js:
            j = j['store_info']
            locator_domain = url
            page_url = api_url
            street_address = j.get('address') if j.get('address') else '<MISSING>'
            location_name = f"{j['name']} {street_address}"
            city = j.get('locality') if j.get('locality') else '<MISSING>'
            state = j.get('region') if j.get('region') else '<MISSING>'
            postal = j.get('postcode') if j.get('postcode') else '<MISSING>'
            country_code = j.get('country') if j.get('country') else '<MISSING>'
            store_number = '<MISSING>'
            phone = j.get('phone') if j.get('phone') else '<MISSING>'
            latitude = j.get('latitude') if j.get('latitude') else '<MISSING>'
            longitude = j.get('longitude') if j.get('longitude') else '<MISSING>'
            location_type = j.get('Type', '<MISSING>')
            hours = j.get('hours') if j.get('hours') else '<MISSING>'

            if hours == '<MISSING>':
                hours_of_operation = hours
            else:
                _tmp = []
                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                for d, line in zip(days, hours.split(';')):
                    start_time = f'{line.split(",")[1][:2]}:{line.split(",")[1][2:]}'
                    end_time = f'{line.split(",")[2][:2]}:{line.split(",")[2][2:]}'
                    _tmp.append(f'{d}: {start_time} - {end_time}')
                hours_of_operation = ';'.join(_tmp)

            row = [locator_domain, page_url, location_name, street_address, city, state, postal,
                   country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

            out.append(row)
        if len(js) < 100:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
