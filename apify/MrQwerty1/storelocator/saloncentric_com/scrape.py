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
    url = 'https://www.blimpie.com/stores/'

    session = SgRequests()
    data = {"request": {
        "appkey": "C8F922C2-35CF-11E3-8171-DA43842CA48B",
        "formdata": {
            "dataview": "store_default",
            "limit": 5000,
            "geolocs": {"geoloc": [{"addressline": "67203", "country": "", "latitude": "", "longitude": ""}]},
            "searchradius": "5000"}}}

    r = session.post('https://hosted.where2getit.com/saloncentric/rest/locatorsearch', data=json.dumps(data))

    js = r.json()['response']['collection']

    for j in js:
        locator_domain = url
        location_name = f"SalonCentric - {j.get('name')} Professional Beauty Supply Store"
        street_address = j.get('address1') or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('state') or '<MISSING>'
        postal = j.get('postalcode') or '<MISSING>'
        country_code = j.get('country') or '<MISSING>'
        store_number = j.get('clientkey')

        # to avoid incorrect ids
        if len(store_number) > 4:
            continue
        phone = j.get('phone') or '<MISSING>'
        latitude = j.get('latitude') or '<MISSING>'
        longitude = j.get('longitude') or '<MISSING>'
        page_url = f"https://stores.saloncentric.com/{state.lower()}/{city.lower()}/{store_number}/"
        location_type = '<MISSING>'

        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        _tmp = []
        for day in days:
            start = j.get(f'{day}_hours_open')
            close = j.get(f'{day}_hours_closed')
            if not start or not close:
                continue
            if start.find('CLOSED') == -1 and close.find('CLOSED') == -1:
                _tmp.append(f'{start} - {close}')
            else:
                _tmp.append(f'{day[:3].upper()}: CLOSED')
        if _tmp:
            hours_of_operation = ';'.join(_tmp)

            if hours_of_operation.count('CLOSED') == 7:
                hours_of_operation = 'CLOSED'
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
