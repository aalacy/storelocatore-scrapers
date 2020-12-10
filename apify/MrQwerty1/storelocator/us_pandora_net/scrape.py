import csv
import json

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
    url = 'https://stores.pandora.net/en-us/'
    api_url = 'https://maps.pandora.net/api/getAsyncLocations?search=75022&level=domain' \
              '&template=domain&limit=5000&radius=5000'

    session = SgRequests()

    r = session.get(api_url)
    js_init = r.json()['maplist']
    line = '[' + js_init.split('<div class=\"tlsmap_list\">')[1].split(',</div>')[0] + ']'
    js = json.loads(line)

    s = set()
    for j in js:
        locator_domain = url
        page_url = j.get('indy_url').replace('//', 'https://') or '<MISSING>'
        location_name = j.get('location_name') or '<MISSING>'
        street_address = f"{j.get('address_1')} {j.get('address_2')}".strip() or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('big_region') or '<MISSING>'
        postal = j.get('post_code') or '<MISSING>'
        country_code = j.get('country') or '<MISSING>'
        if country_code != 'US':
            continue
        store_number = j.get('fid') or '<MISSING>'
        phone = j.get('local_phone') or '<MISSING>'
        latitude = j.get('lat') or '<MISSING>'
        longitude = j.get('lng') or '<MISSING>'
        location_type = j.get('Store Type_CS') or '<MISSING>'

        _tmp = []
        tmp_js = json.loads(j.get('hours_sets:primary')).get('days', {})
        for day in tmp_js.keys():
            line = tmp_js[day]
            if len(line) == 1:
                start = line[0]['open']
                close = line[0]['close']
                _tmp.append(f'{day} {start} - {close}')
            else:
                _tmp.append(f'{day} Closed')

        if _tmp:
            hours_of_operation = ';'.join(_tmp)
        else:
            hours_of_operation = '<MISSING>'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

        line = f"{location_name} {street_address} {city} {state} {postal}"
        if line not in s:
            s.add(line)
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
