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
    url = 'https://expresspros.com'

    session = SgRequests()
    data = {'Radius': '50000', 'Latitude': '40.7127753', 'Longitude': '-74.0059728'}

    r = session.post('https://workforce.expresspros.com/locations/findlocations', data=data)
    js = r.json()['Locations']
    for j in js:
        locator_domain = url
        street_address = f"{j.get('AddressLine1')} {j.get('AddressLine2') or ''}".strip() or '<MISSING>'
        city = j.get('CityName') or '<MISSING>'
        state = j.get('StateAbbr') or '<MISSING>'
        postal = j.get('PostalCode') or '<MISSING>'
        if len(postal) == 5 or postal.find('-') != -1:
            country_code = 'US'
        else:
            country_code = 'CA'
        store_number = j.get('OfficeNumber') or '<MISSING>'
        page_url = f"{url}/{j.get('WebPath')}"
        location_name = j.get('OfficeName') or '<MISSING>'
        phone = j.get('MainPhone') or '<MISSING>'
        latitude = j.get('Latitude') or '<MISSING>'
        longitude = j.get('Longitude') or '<MISSING>'
        location_type = '<MISSING>'
        hours_of_operation = '<MISSING>'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
