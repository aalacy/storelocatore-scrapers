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


def get_js(param):
    session = SgRequests()
    data = {"request": {
        "appkey": "6E3ECEB6-B58F-11E6-9AC3-9C37D1784D66",
        "formdata": {
            "dataview": "store_default",
            "limit": 5000,
            "geolocs": {"geoloc": [{"addressline": param['addressline'], "country": "", "latitude": "", "longitude": ""}]},
            "searchradius": "3000", 'where': {'country': {'eq': param['country']}}}}}

    r = session.post('https://hosted.where2getit.com/michaels/rest/locatorsearch', data=json.dumps(data))
    js = r.json()['response']['collection']
    return js


def fetch_data():
    out = []
    s = set()
    url = 'https://www.michaels.com/store-locator'
    params = [
        {'addressline': 'T9H 4G9', 'country': 'CA'},
        {'addressline': '99507', 'country': 'US'},
        {'addressline': '30313', 'country': 'US'},
        {'addressline': '84602', 'country': 'US'}
    ]

    for p in params:
        js = get_js(p)
        for j in js:
            locator_domain = url
            location_name = f"Michaels, {j.get('name')}"
            street_address = j.get('address1') or '<MISSING>'
            city = j.get('city') or '<MISSING>'
            postal = j.get('postalcode') or '<MISSING>'
            country_code = j.get('country') or '<MISSING>'
            if country_code == 'CA':
                state = j.get('province') or '<MISSING>'
            else:
                state = j.get('state') or '<MISSING>'
            store_number = j.get('clientkey')
            if store_number in s:
                continue

            s.add(store_number)
            phone = j.get('phone') or '<MISSING>'
            latitude = j.get('latitude') or '<MISSING>'
            longitude = j.get('longitude') or '<MISSING>'
            page_url = f"http://locations.michaels.com/{state.lower()}/{city.lower()}/{store_number}/"
            location_type = '<MISSING>'

            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            _tmp = []
            for day in days:
                line = j.get(f'{day[:3]}_hrs_special')
                _tmp.append(f"{day.capitalize()}: {line}")
            if _tmp:
                hours_of_operation = ';'.join(_tmp)
    
                if hours_of_operation.count('None') == 7:
                    hours_of_operation = 'Temporarily Closed'
            else:
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
