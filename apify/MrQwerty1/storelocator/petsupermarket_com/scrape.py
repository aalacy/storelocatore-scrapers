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
    url = 'https://petsupermarket.com/'

    headers = {'x-api-key': 'iOr0sBW7MGBg8BDTPjmBOYdCthN3PdaJ'}
    params = (('clientId', '5e3da261df2763dd5ce605ab^'), ('cname', 'storelocator.petsupermarket.com'))
    api_url = 'https://gannett-production.apigee.net/store-locator-next/5f6371889ed7b3da617c02b5/locations-details'
    session = SgRequests()
    r = session.get(api_url, headers=headers, params=params)
    js = r.json()['features']
    for j in js:
        g = j['geometry']['coordinates']
        j = j['properties']
        locator_domain = url
        page_url = f"https://storelocator.petsupermarket.com/{j.get('slug')}"
        location_name = j.get('name') or '<MISSING>'
        street_address = f"{j.get('addressLine1')} {j.get('addressLine2') or ''}" or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('province') or '<MISSING>'
        postal = j.get('postalCode') or '<MISSING>'
        country_code = j.get('country') or '<MISSING>'
        store_number = j.get('branch') or '<MISSING>'
        phone = j.get('phoneLabel') or '<MISSING>'
        if g:
            latitude = g[1]
            longitude = g[0]
        else:
            latitude = '<MISSING>'
            longitude = '<MISSING>'
        location_type = '<MISSING>'

        hours = j.get('hoursOfOperation') or '<MISSING>'
        if hours == '<MISSING>':
            hours_of_operation = hours
        else:
            _tmp = []
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for d in days:
                start = hours.get(d)[0][0]
                close = hours.get(d)[0][1]
                _tmp.append(f'{d}: {start} - {close}')

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
