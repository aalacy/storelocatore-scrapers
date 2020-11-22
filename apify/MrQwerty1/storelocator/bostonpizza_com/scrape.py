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
    url = 'https://bostonpizza.com/'
    api_url = 'https://bostonpizza.com/content/bostonpizza/jcr:content/leftnavigation.en.getAllStores.json'

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        locator_domain = url
        page_url = f'https://bostonpizza.com/en/locations/{j.get("restaurantJcrName")}.html'
        location_name = j.get('restaurantName').strip()
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip() or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('province') or '<MISSING>'
        postal = j.get('postalCode') or '<MISSING>'
        country_code = 'CA'
        store_number = j.get('storeId') or '<MISSING>'
        phone = j.get('restaurantPhoneNumber')[3:] or '<MISSING>'
        latitude = j.get('latitude') or '<MISSING>'
        longitude = j.get('longitude') or '<MISSING>'
        location_type = j.get('bpType') or '<MISSING>'

        _tmp = []
        hours = j.get('storeHours', {}).get('DayList')
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for h, d in zip(hours, days):
            start = h.get('TimeOpen')[:-3]
            close = h.get('TimeClose')[:-3]
            _tmp.append(f'{d.capitalize()}: {start} - {close}')

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
