import csv
import html

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
    url = 'https://ca.burberry.com/store-locator/canada/'

    session = SgRequests()
    r = session.get(f'https://api.burberry.com/services/sites/v1?&country=ca&limit=1000')
    js = r.json()['data']

    for j in js:
        locator_domain = url
        a = j.get('address', {})
        street_address = a.get('line2') or '<MISSING>'
        city = a.get('city') or '<MISSING>'
        location_name = html.unescape(f"{city} {j.get('public_name_en')}")
        state = a.get('state') or '<MISSING>'
        postal = a.get('postcode') or '<MISSING>'
        country_code = a.get('country') or '<MISSING>'
        store_number = j.get('id') or '<MISSING>'
        page_url = f"https://ca.burberry.com/store-locator/canada/-/{store_number}"
        phone = j.get('phone') or '<MISSING>'
        latitude = j.get('latitude') or '<MISSING>'
        longitude = j.get('longitude') or '<MISSING>'
        location_type = j.get('type') or '<MISSING>'
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        _tmp = []
        for d in days:
            line = j['opening_times'][d]
            if line:
                start = line['hours'][0]['from']
                close = line['hours'][0]['to']
                if not start or not close:
                    _tmp.append(f"{d[:3].capitalize()}: closed")
                else:
                    _tmp.append(f"{d[:3].capitalize()}: {start} - {close}")

        hours_of_operation = ';'.join(_tmp) or '<MISSING>'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
