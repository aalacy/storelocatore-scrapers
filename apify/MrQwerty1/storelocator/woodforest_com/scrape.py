import csv
import sgzip

from concurrent.futures import ThreadPoolExecutor, as_completed
from sgrequests import SgRequests
from sgzip import SearchableCountries


def write_output(data):
    with open('data.csv', mode='w', encoding='utf8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        for row in data:
            writer.writerow(row)


def get_data(postal):
    _tmp_out = []
    session = SgRequests()
    locator_domain = 'https://woodforest.com/'
    api_url = f'https://woodforest.com/Lib/WFNB.Functions.GetLocations.ashx?address=' \
              f'&city=&state=&zipCode={postal}&distance=30&display=45'

    r = session.get(api_url)
    js = r.json().get('locations') or []
    for j in js:
        a = j.get('address', {})
        street_address = a.get('street') or '<MISSING>'
        city = a.get('city') or '<MISSING>'
        state = a.get('state') or '<MISSING>'
        postal = a.get('zipCode') or '<MISSING>'
        country_code = 'US'
        location_name = j.get('institution', {}).get('name') or '<MISSING>'
        store_number = j.get('number') or '<MISSING>'
        phone = j.get('phone') or '<MISSING>'
        g = a.get('coordinates', {})
        latitude = g.get('latitude') or '<MISSING>'
        longitude = g.get('longitude') or '<MISSING>'
        location_type = j.get('type', {}).get('displayAs') or '<MISSING>'
        page_url = f'https://woodforest.com/Home/About-Us/Contact-Us/Locations/SearchResults.aspx' \
                   f'#address=&city=&state=&zipCode={postal}&distance=30'

        hours = j.get('lobby')
        _tmp = []
        for h in hours:
            day = h.get('day')
            status = h.get('status')
            if status == 'Closed':
                _tmp.append(f'{day}: Closed')
            else:
                formated = h.get('formattedHours')
                _tmp.append(f'{day}: {formated}')

        hours_of_operation = ';'.join(_tmp) or '<MISSING>'

        if hours_of_operation.count('Closed') == 7:
            hours_of_operation = 'Closed'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        _tmp_out.append(row)
    return _tmp_out


def fetch_data():
    out = []
    s = set()
    threads = []
    zips = sgzip.for_radius(radius=30, country_code=SearchableCountries.USA)

    with ThreadPoolExecutor(max_workers=1) as executor:
        for postal in zips:
            threads.append(executor.submit(get_data, postal))

    for task in as_completed(threads):
        _tmp = task.result()
        for t in _tmp:
            line = ';'.join(t[2:6])
            if line not in s:
                s.add(line)
                out.append(t)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
