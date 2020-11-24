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
    url = 'https://www.arco.com'
    api_url = 'https://www.arco.com/img/findstation/MasterArcoStoreLocations.csv'

    session = SgRequests()
    r = session.get(api_url)
    dr = csv.DictReader(r.content.decode('utf8').splitlines())

    s = set()
    n = set()
    for j in dr:
        locator_domain = url
        page_url = '<MISSING>'
        location_name = j.get('StoreName').strip()
        street_address = j.get('Address').strip() or '<MISSING>'
        city = j.get('City').strip() or '<MISSING>'
        state = j.get('State').strip() or '<MISSING>'
        postal = j.get('Zip') or '<MISSING>'
        country_code = 'US'
        store_number = j.get('StoreNumber') or '<MISSING>'
        phone = j.get('Phone').strip() or '<MISSING>'
        latitude = j.get('Lat').strip() or '<MISSING>'
        longitude = j.get('Lng').strip() or '<MISSING>'
        location_type = '<MISSING>'
        hours_of_operation = '<MISSING>'

        # to avoid non us stores
        if len(state) > 2 or phone.startswith('52 ') or latitude.find('.') == -1:
            continue

        line = (street_address, city, state, postal)
        if line in s or store_number in n:
            continue

        s.add(line)
        n.add(store_number)
        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
