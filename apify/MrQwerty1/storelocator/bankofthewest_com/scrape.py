import csv
from sgrequests import SgRequests


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []
    url = 'https://www.bankofthewest.com/customer-service/branch-results.html'
    api_url = 'https://www.bankofthewest.com/api/branches/GetByDistanceMobile'

    session = SgRequests()
    headers = {'Content-Type': 'application/json'}

    data = '{"lat":"41.1399814","lon":"-104.8202462","rad":100000,"btype":true,"mlofficer":false,"atm":true}'

    r = session.post(api_url, headers=headers, data=data)
    js = r.json()

    for j in js:
        locator_domain = url
        page_url = j.get('HomepageUrl') or '<MISSING>'
        location_name = f'Bank of West {j.get("Name")}'.strip()
        street_address = j.get('Address') or '<MISSING>'
        city = j.get('City') or '<MISSING>'
        state = j.get('State') or '<MISSING>'
        postal = j.get('Zipcode') or '<MISSING>'
        country_code = 'US'
        if page_url == '<MISSING>':
            store_number = location_name.split('#')[-1]
        else:
            store_number = page_url.split('/')[-1].split('-')[0]
        phone = j.get('PhoneNumber') or '<MISSING>'
        latitude = j.get('Latitude') or '<MISSING>'
        longitude = j.get('Longitude') or '<MISSING>'
        hours_of_operation = j.get('WeekdayHours') or '<MISSING>'
        location_type = j.get('Type', '<MISSING>')

        def generate_row(_type):
            return [locator_domain, page_url, location_name, street_address, city, state, postal, country_code,
                    store_number, phone, _type, latitude, longitude, hours_of_operation]

        if location_type == 'atmbranch':
            out.append(generate_row('atm'))
            out.append(generate_row('branch'))
        else:
            out.append(generate_row(location_type))

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
