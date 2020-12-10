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
    url = 'https://locations.firstcitizens.com/'

    session = SgRequests()
    headers = {'Accept': 'application/json'}

    s = set()
    for i in range(0, 100000, 50):
        r = session.get(f'https://locations.firstcitizens.com/search?q=&all=true&l=en&offset={i}', headers=headers)
        js = r.json()['response']['entities']
        for jj in js:
            j = jj.get('profile')
            a = j.get('address')
            locator_domain = url
            street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip() or '<MISSING>'
            city = a.get('city') or '<MISSING>'
            state = a.get('region') or '<MISSING>'
            postal = a.get('postalCode') or '<MISSING>'
            country_code = a.get('countryCode') or '<MISSING>'
            store_number = '<MISSING>'
            page_url = j.get('c_pagesURL') if j.get('c_pagesURL') else j.get('websiteUrl') or '<MISSING>'
            if page_url.find('-atm') == -1:
                location_name = j.get('geomodifier') or j.get('c_friendlyName')
            else:
                location_name = f"{city} - ATM"
            phone = j.get('mainPhone', {}).get('display') or '<MISSING>'
            latitude = j.get('yextDisplayCoordinate', {}).get('lat') or '<MISSING>'
            longitude = j.get('yextDisplayCoordinate', {}).get('long') or '<MISSING>'
            location_type = j.get('c_lOB') or '<MISSING>'

            hours = j.get('hours', {}).get('normalHours', [])
            _tmp = []
            for h in hours:
                day = h.get('day')
                if not h.get('isClosed'):
                    interval = h.get('intervals')
                    start = str(interval[0].get('start'))
                    if len(start) == 3:
                        start = f'0{start}'
                    elif len(start) == 1:
                        start = f'000{start}'
                    end = str(interval[0].get('end'))
                    line = f"{day[:3].capitalize()}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
                    if line.find('00:00') != -1:
                        line = f'{day[:3].capitalize()}: Open 24 Hours'
                else:
                    line = f'{day[:3].capitalize()}: Closed'
                _tmp.append(line)

            hours_of_operation = ';'.join(_tmp) or '<MISSING>'
            if hours_of_operation.count('Closed') == 7:
                hours_of_operation = 'Closed'

            line = (location_name, street_address, city, state, postal)
            row = [locator_domain, page_url, location_name, street_address, city, state, postal,
                   country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
            if line not in s:
                out.append(row)
                s.add(line)
        if len(js) < 50:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
