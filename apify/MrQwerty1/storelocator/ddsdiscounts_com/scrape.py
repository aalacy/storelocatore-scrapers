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


def get_js():
    session = SgRequests()
    data = {"request": {
        "appkey": "4E0CC702-70E5-11E8-923C-16F58D89CD5A",
        "formdata": {
            "dataview": "store_default",
            "limit": 5000,
            "geolocs": {"geoloc": [{"addressline": "30313", "country": "", "latitude": "", "longitude": ""}]},
            "searchradius": "5000", 'where': {'country': {'eq': "US"}}}}}

    r = session.post('https://hosted.where2getit.com/ddsdiscounts/rest/locatorsearch', data=json.dumps(data))
    js = r.json()['response']['collection']
    return js


def fetch_data():
    out = []
    url = 'https://ddsdiscounts.com/'
    js = get_js()
    for j in js:
        locator_domain = url
        location_name = f"{j.get('name1')}"
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip() or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        postal = j.get('postalcode') or '<MISSING>'
        country_code = j.get('country') or '<MISSING>'
        state = j.get('state') or '<MISSING>'
        store_number = j.get('clientkey')
        phone = j.get('phone') or '<MISSING>'
        latitude = j.get('latitude') or '<MISSING>'
        longitude = j.get('longitude') or '<MISSING>'
        page_url = "<MISSING>"
        location_type = '<MISSING>'

        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        _tmp = []
        for day in days:
            _tmp.append(f'{day.capitalize()} {j.get(f"{day}")}')

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
