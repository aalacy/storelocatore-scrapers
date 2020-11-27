import csv

from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open('data.csv', mode='w', encoding='utf8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        for row in data:
            writer.writerow(row)


def get_hours(url):
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)
    try:
        hours = ''.join(tree.xpath("//h2[@style='font-size: 18px; color: #0b2e4d;']")[0].xpath('./text()')) \
        .replace(',', ':').replace('\n', '').replace('PM', 'PM;').replace('Oct 30 - Dec 6', '').strip() or '<MISSING>'
    except IndexError:
        hours = '<MISSING>'
    print(hours)
    return hours


def fetch_data():
    out = []
    url = 'https://athome.com/'
    api_url = 'https://www.athome.com/on/demandware.store/Sites-athome-sfra-Site/default/Stores-FindStores?showMap' \
              '=true&radius=5000&lat=40.7127753&long=-74.0059728'

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()['stores']

    for j in js:
        locator_domain = url
        page_url = f'https://www.athome.com/store-detail/?StoreID={j.get("ID")}'
        location_name = j.get('name').strip()
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip() or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('stateCode') or '<MISSING>'
        postal = j.get('postalCode') or '<MISSING>'
        country_code = j.get('countryCode') or '<MISSING>'
        store_number = '<MISSING>'
        phone = j.get('phone') or '<MISSING>'
        if phone.find('Coming') != -1:
            continue
        latitude = j.get('latitude') or '<MISSING>'
        longitude = j.get('longitude') or '<MISSING>'
        location_type = '<MISSING>'
        hours_of_operation = get_hours(page_url)

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
