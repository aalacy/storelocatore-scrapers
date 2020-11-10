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
    url = 'https://www.carstar.ca/en/locations/'
    api_url = 'https://api.carstar.ca/api/stores/'

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()['message']['stores']

    for j in js:
        locator_domain = url
        page_url = api_url
        location_name = j.get('storeName')
        street_address = j.get('streetAddress1') or '<MISSING>'
        city = j.get('locationCity') or '<MISSING>'
        state = j.get('locationState') or '<MISSING>'
        postal = j.get('locationPostalCode').encode("ascii", "ignore").decode() or '<MISSING>'
        country_code = 'CA'
        store_number = j.get('storeId') or '<MISSING>'
        phone = j.get('phone').encode("ascii", "ignore").decode() or '<MISSING>'
        latitude = j.get('latitude') or '<MISSING>'
        longitude = j.get('longitude') or '<MISSING>'
        hours_of_operation = '<INACCESSIBLE>'
        location_type = j.get('Type', '<MISSING>')

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
