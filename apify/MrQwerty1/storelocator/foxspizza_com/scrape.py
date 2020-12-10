import csv
import usaddress

from concurrent.futures import ThreadPoolExecutor, as_completed
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


def get_urls():
    session = SgRequests()
    r = session.get('https://www.foxspizza.com/store-sitemap.xml')
    tree = html.fromstring(r.content)
    return tree.xpath("//loc/text()")


def get_data(url):
    locator_domain = 'https://foxspizza.com/'
    page_url = url
    tag = {'Recipient': 'recipient', 'AddressNumber': 'address1', 'AddressNumberPrefix': 'address1',
           'AddressNumberSuffix': 'address1', 'StreetName': 'address1', 'StreetNamePreDirectional': 'address1',
           'StreetNamePreModifier': 'address1', 'StreetNamePreType': 'address1',
           'StreetNamePostDirectional': 'address1',
           'StreetNamePostModifier': 'address1', 'StreetNamePostType': 'address1', 'CornerOf': 'address1',
           'IntersectionSeparator': 'address1', 'LandmarkName': 'address1', 'USPSBoxGroupID': 'address1',
           'USPSBoxGroupType': 'address1', 'USPSBoxID': 'address1', 'USPSBoxType': 'address1',
           'BuildingName': 'address2', 'OccupancyType': 'address2', 'OccupancyIdentifier': 'address2',
           'SubaddressIdentifier': 'address2', 'SubaddressType': 'address2', 'PlaceName': 'city', 'StateName': 'state',
           'ZipCode': 'postal'}

    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)

    location_name = ''.join(tree.xpath("//h5[@class='blog_title']//text()")).strip()
    line = ''.join(tree.xpath("//h6[@class='loc_address']/text()")).strip()
    if not line:
        return
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == 'None':
        street_address = '<MISSING>'
    city = a.get('city') or '<MISSING>'
    state = a.get('state') or '<MISSING>'
    postal = a.get('postal') or '<MISSING>'
    country_code = 'US'
    store_number = '<MISSING>'
    phone = ''.join(tree.xpath("//span[@class='phone_no']/a/text()")).strip()
    location_type = '<MISSING>'
    latitude = '<MISSING>'
    longitude = '<MISSING>'
    hours_of_operation = ';'.join(tree.xpath("//span[@class='ad1']/text()")) or '<MISSING>'

    row = [locator_domain, page_url, location_name, street_address, city, state, postal,
           country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
    return row


def fetch_data():
    out = []
    threads = []
    urls = get_urls()

    with ThreadPoolExecutor(max_workers=10) as executor:
        for url in urls:
            threads.append(executor.submit(get_data, url))

    for task in as_completed(threads):
        row = task.result()
        if row:
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
