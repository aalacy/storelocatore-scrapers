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


def get_hours(url, _type):
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)
    if _type.lower().find('delivery') != -1:
        hours = ';'.join(tree.xpath("//div[@class='delHours']/p/text()"))
    else:
        hours = ''.join(tree.xpath("//span[@class='gcTableCell'and ./h3[contains(text(), 'Food')]]/p/text()")).strip()

    return hours.replace('\n', '') if hours else '<MISSING>'


def fetch_data():
    out = []
    url = 'https://rasushi.com/locations/'
    api_url = 'https://rasushi.com/wp-admin/admin-ajax.php'

    session = SgRequests()
    data = {'action': 'get_all_stores'}
    r = session.post(api_url, data=data)
    js = r.json().values()

    for j in js:
        locator_domain = url
        page_url = j.get('gu')
        location_name = j.get('na')
        street_address = j.get('st') or '<MISSING>'
        city = j.get('ct') or '<MISSING>'
        state = j.get('rg') or '<MISSING>'

        # one of the records has incorrect "state" value
        if len(state) != 2:
            state = location_name.split(',')[-1].strip()

        postal = j.get('zp') or '<MISSING>'
        country_code = j.get('co') or '<MISSING>'
        store_number = j.get('storeId') or '<MISSING>'
        phone = j.get('te') or '<MISSING>'
        latitude = j.get('lat') or '<MISSING>'
        longitude = j.get('lng') or '<MISSING>'
        location_type = j.get('ca', {}).get('0') or '<MISSING>'
        hours_of_operation = get_hours(page_url, location_type)

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

        out.append(row)
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
