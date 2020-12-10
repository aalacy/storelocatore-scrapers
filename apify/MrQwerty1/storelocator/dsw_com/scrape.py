import csv
from sgrequests import SgRequests


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        for row in data:
            writer.writerow(row)


def generate_links():
    r = session.get('https://stores.dsw.com/usa.json')
    js = r.json()['directoryHierarchy']

    urls = list(get_urls(js))

    return urls


def get_urls(states):
    for state in states.values():
        children = state['children']
        if children is None:
            yield f"https://stores.dsw.com/{state['url']}".replace('.html', '.json')
        else:
            yield from get_urls(children)


def fetch_data():
    out = []
    urls = generate_links()
    locator_domain = 'https://stores.dsw.com/index.html'

    for url in urls:
        r = session.get(url)
        j = r.json()
        page_url = url.replace('.json', '.html')
        mod = j.get('displayAddress') or j.get('customByName', {}).get('Geomodifier', '')
        location_name = f"{j.get('name')} {mod or ''}".strip() or '<MISSING>'
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip() or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('state') or '<MISSING>'
        postal = j.get('postalCode') or '<MISSING>'
        country_code = j.get('country') or '<MISSING>'
        store_number = '<MISSING>'
        phone = j.get('phone') or '<MISSING>'
        latitude = j.get('latitude') or '<MISSING>'
        longitude = j.get('longitude') or '<MISSING>'
        location_type = '<MISSING>'
        days = j.get('hours', {}).get('days') or '<MISSING>'
        if days == '<MISSING>':
            hours_of_operation = days
        else:
            _tmp = []
            for d in days:
                day = d.get('day')[:3].capitalize()
                start, end = '0', '0'
                interval = d.get('intervals')
                if interval:
                    start = str(interval[0].get('start', '0'))
                    end = str(interval[0].get('end', '0'))

                    # normalize 9:30 -> 09:30
                    if len(start) == 3:
                        start = f'0{start}'

                if start != '0' and end != '0':
                    line = f'{day}  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}'
                else:
                    line = f'{day}  Closed'
                _tmp.append(line)
            hours_of_operation = ';'.join(_tmp) or '<MISSING>'

            if hours_of_operation.count('Closed') == 7:
                hours_of_operation = 'Closed'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    session = SgRequests()
    links = generate_links()
    scrape()
