import csv
import json
from concurrent import futures
from sgrequests import SgRequests
from sgzip.static import static_zipcode_list, SearchableCountries


def write_output(data):
    with open('data.csv', mode='w', encoding='utf8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        for row in data:
            writer.writerow(row)


def get_data(_zip):
    rows = []
    locator_domain = 'https://www.moneypass.com/'
    page_url = 'https://www.moneypass.com/atm-locator.html'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': '*/*',
        'Accept-Language': 'uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3',
        'Content-Type': 'application/json; charset=UTF-8',
        'Origin': 'https://moneypasslocator.wave2.io',
        'Connection': 'keep-alive',
        'Referer': 'https://moneypasslocator.wave2.io/',
        'TE': 'Trailers',
    }

    data = {"Latitude": "", "Longitude": "", "Address": _zip, "City": "", "State": "", "Zipcode": "", "Country": "",
            "Action": "textsearch", "ActionOverwrite": "", "Filters": "ATMSF,ATMDP,HAATM,247ATM,"}

    session = SgRequests()
    r = session.post('https://locationapi.wave2.io/api/client/getlocations', headers=headers, data=json.dumps(data))
    js = r.json()['Features']

    for j in js:
        a = j.get('Properties')
        location_name = a.get('LocationName') or '<MISSING>'
        street_address = a.get('Address') or '<MISSING>'
        city = a.get('City') or '<MISSING>'
        state = a.get('State') or '<MISSING>'
        postal = a.get('Postalcode') or '<MISSING>'
        if postal == '0':
            postal = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        phone = '<MISSING>'
        latitude = a.get('Latitude') or '<MISSING>'
        longitude = a.get('Longitude') or '<MISSING>'
        location_type = a.get('LocationCategory') or '<MISSING>'
        hours_of_operation = j.get('LocationFeatures').get('TwentyFourHours') or '<MISSING>'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    postals = static_zipcode_list(radius=20, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, postal): postal for postal in postals}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                check = tuple(row[2:6])
                if check not in s:
                    s.add(check)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
