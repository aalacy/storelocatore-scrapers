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


def get_clean_hoo(hoo):
    return hoo.replace('<br>', ';').replace('<', '').replace('>', '').replace('br', '').replace('\n', '')


def fetch_data():
    out = []
    url = 'https://www.rainbowshops.com/store-locator'

    for i in range(0, 10000, 200):
        session = SgRequests()
        r = session.get(f'https://www.rainbowshops.com/s/rainbow/dw/shop/v19_10/stores?client_id=5a2fe18e-5bc7-4512'
                        f'-8c1e-f1b231245f8c&max_distance=5000&latitude=33.02&longitude=-97.12&count=200&start={i}')
        js = r.json()['data']

        for j in js:
            locator_domain = url
            store_number = j.get('id') or '<MISSING>'
            page_url = f"https://www.rainbowshops.com/store-details?storeid={store_number}"
            location_name = f"Rainbow, Store Number {int(store_number)}"
            street_address = j.get('address1') or '<MISSING>'
            city = j.get('city') or '<MISSING>'
            state = j.get('state_code') or '<MISSING>'
            # to avoid garbage value
            if len(state) > 2:
                state = state[:2]
            postal = j.get('postal_code') or '<MISSING>'
            country_code = j.get('country_code') or '<MISSING>'
            phone = j.get('phone') or '<MISSING>'
            latitude = j.get('latitude') or '<MISSING>'
            longitude = j.get('longitude') or '<MISSING>'
            location_type = j.get('_type', '<MISSING>')
            hours_of_operation = get_clean_hoo(j.get('store_hours', '')) or '<MISSING>'

            row = [locator_domain, page_url, location_name, street_address, city, state, postal,
                   country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
            out.append(row)

        if len(js) < 200:
            break
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
