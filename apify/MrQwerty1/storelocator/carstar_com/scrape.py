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
    url = 'https://www.carstar.com/locations/'
    api_url = 'https://api.carstar.com/api/stores/'

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()['message']['stores']

    for j in js:
        locator_domain = url
        page_url = api_url
        location_name = j.get('storeName')
        street_address = j.get('streetAddress1') if j.get('streetAddress1') else '<MISSING>'
        city = j.get('locationCity') if j.get('locationCity') else '<MISSING>'
        state = j.get('locationState') if j.get('locationState') else '<MISSING>'
        postal = j.get('locationPostalCode') if j.get('locationPostalCode') else '<MISSING>'
        if len(postal) == 4:
            postal = f'0{postal}'
        country_code = 'US'
        store_number = j.get('storeId') if j.get('storeId') else '<MISSING>'
        phone = j.get('phone') if j.get('phone') else '<MISSING>'
        latitude = j.get('latitude') if j.get('latitude') else '<MISSING>'
        longitude = j.get('longitude') if j.get('longitude') else '<MISSING>'
        hours_of_operation = '<INACCESSIBLE>'
        location_type = j.get('Type', '<MISSING>')

        uniq = (location_name, street_address, city, state, postal, phone, location_type, latitude, longitude)

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

        if uniq not in s:
            s.add(uniq)
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
