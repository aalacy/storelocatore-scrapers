import csv
import usaddress

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


def fetch_data():
    out = []
    url = 'https://lincare.com/'
    api_url = 'http://www.lincare.com/Location-Map/moduleId/2040/controller/Location/action/LocationList' \
              '?searchAddress=75022&searchState=&distanceRange=50000'
    tag = {'Recipient': 'recipient', 'AddressNumber': 'address1', 'AddressNumberPrefix': 'address1',
           'AddressNumberSuffix': 'address1', 'StreetName': 'address1', 'StreetNamePreDirectional': 'address1',
           'StreetNamePreModifier': 'address1', 'StreetNamePreType': 'address1', 'StreetNamePostDirectional': 'address1',
           'StreetNamePostModifier': 'address1', 'StreetNamePostType': 'address1', 'CornerOf': 'address1',
           'IntersectionSeparator': 'address1', 'LandmarkName': 'address1', 'USPSBoxGroupID': 'address1',
           'USPSBoxGroupType': 'address1', 'USPSBoxID': 'address1', 'USPSBoxType': 'address1',
           'BuildingName': 'address2', 'OccupancyType': 'address2', 'OccupancyIdentifier': 'address2',
           'SubaddressIdentifier': 'address2', 'SubaddressType': 'address2', 'PlaceName': 'city', 'StateName': 'state',
           'ZipCode': 'postal'}

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[@class='locator-store-info']")

    for d in div:
        locator_domain = url
        page_url = api_url
        location_name = '-'.join(''.join(d.xpath('./h3/text()')).strip().split('-')[1:])
        location_name = ' '.join(location_name.split()).strip()
        adr_line1 = ' '.join(d.xpath(".//div[@class='address']/text()")).strip()
        adr_line2 = ''.join(d.xpath(".//div[@class='address']/div[1]/text()")).strip()
        line = f'{adr_line1} {adr_line2}'
        line = ' '.join(line.split())
        try:
            a = usaddress.tag(line, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
            city = a.get('city') or '<MISSING>'
            if city == 'RICHMOND HILL':
                raise Exception
            state = a.get('state') or '<MISSING>'
            postal = a.get('postal') or '<MISSING>'
        except:
            street_address = ' '.join(adr_line1.split())
            city = adr_line2.split(',')[0]
            state = adr_line2.split(',')[1].strip()[:2]
            postal = adr_line2.replace(city, '').replace(state, '').replace(',', '').replace(' ', '').strip()

        country_code = 'US'
        if city == 'RICHMOND HILL':
            country_code = 'CA'
            postal = postal.replace('-', ' ')
        store_number = '<MISSING>'
        phone = ''.join(d.xpath(".//div[@class='address']/div[contains(text(), 'Phone')]/text()")).strip()
        if phone:
            phone = phone.split()[-1]
        else:
            phone = '<MISSING>'
        latitude = '<MISSING>'
        longitude = '<MISSING>'
        location_type = '<MISSING>'
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
