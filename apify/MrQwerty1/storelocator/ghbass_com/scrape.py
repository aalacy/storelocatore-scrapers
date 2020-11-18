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
    url = 'https://www.ghbass.com/store-locator/all-stores.do'

    session = SgRequests()

    for i in range(0, 100000, 5):
        r = session.get(f'https://www.ghbass.com/store-locator/ajax-search.do?method=search&address=75022&PageIndex={i}')
        js = r.json()['results']
        for j in js:
            a = j.get('address')
            locator_domain = url
            street_address = f"{a.get('street1')} {a.get('street2') or ''}".strip() or '<MISSING>'
            city = a.get('city') or '<MISSING>'
            location_name = f"{j.get('name')}"
            state = a.get('stateCode') or '<MISSING>'
            postal = a.get('postalCode') or '<MISSING>'
            country_code = a.get('countryName') or '<MISSING>'
            store_number = '<MISSING>'
            page_url = f"https://www.ghbass.com{j.get('link')}" or '<MISSING>'
            phone = a.get('phone') or '<MISSING>'
            g = j.get('location', {})
            latitude = g.get('latitude') or '<MISSING>'
            longitude = g.get('longitude') or '<MISSING>'
            location_type = '<MISSING>'

            hours_of_operation = '<MISSING>'

            row = [locator_domain, page_url, location_name, street_address, city, state, postal,
                   country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
            out.append(row)
        if len(js) < 5:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
