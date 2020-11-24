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
    url = 'https://impark.com/'
    api_url = 'https://lots.impark.com/api/lots/IMP/EN?latLoc=55.87&lngLoc=-77.64&latMin=0&lngMin=-180&latMax=90&lngMax=180'

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        locator_domain = url
        a = j.get('address')
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip() or '<MISSING>'
        city = a.get('city') or '<MISSING>'
        state = a.get('provState') or '<MISSING>'
        postal = a.get('postalCode') or '<MISSING>'
        country_code = a.get('country') or '<MISSING>'
        if country_code == 'Canada':
            country_code = 'CA'
        else:
            country_code = 'US'
        # store_number = f'{j.get("branchNumber")},{j.get("lotNumber")}' or '<MISSING>'
        store_number = '<MISSING>'
        page_url = f'https://lots.impark.com/imp/en#details={j.get("branchNumber")},{j.get("lotNumber")}'
        location_name = f"{j.get('lotName')} - Lot #{j.get('lotNumber')}"
        phone = '<MISSING>'
        loc = j.get('location')
        latitude = loc.get('lat') or '<MISSING>'
        longitude = loc.get('lng') or '<MISSING>'
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
