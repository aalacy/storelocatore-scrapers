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
    url = 'https://graybar.com/'

    session = SgRequests()
    headers = {'Accept': 'application/json'}

    for i in range(0, 100000):
        r = session.get(f'https://www.graybar.com/store-finder?q=&page={i}&latitude=38.6994076&longitude=-90.4384332',
                        headers=headers)
        js = r.json()['data']
        for j in js:
            locator_domain = url
            location_name = j.get('displayName') or '<MISSING>'
            street_address = f"{j.get('line1')} {j.get('line2') or ''}".strip() or '<MISSING>'
            city = j.get('town') or '<MISSING>'
            state = j.get('region') or '<MISSING>'
            postal = j.get('postalCode') or '<MISSING>'
            country_code = 'US'
            store_number = '<MISSING>'
            page_url = '<MISSING>'
            phone = j.get('phone') or '<MISSING>'
            latitude = j.get('latitude') or '<MISSING>'
            longitude = j.get('longitude') or '<MISSING>'

            hours = j.get('openingHours') or []
            for h in hours:
                location_type = h.get('type')
                times = h.get('times')
                _tmp = []
                for t in times:
                    day = t.get('weekDay')
                    opening = t.get('opening')
                    close = t.get('closing')
                    if opening:
                        _tmp.append(f'{day}: {opening} - {close}')
                    else:
                        _tmp.append(f'{day}: Closed')

                hours_of_operation = ';'.join(_tmp)

                if hours_of_operation.count('Closed') == 7:
                    continue
                else:
                    row = [locator_domain, page_url, location_name, street_address, city, state, postal,
                           country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
                    out.append(row)
        if len(js) < 10:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
