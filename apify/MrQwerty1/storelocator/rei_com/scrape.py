import csv
import json

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


def get_json(url):
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)
    j = ''.join(tree.xpath("//script[@id='modelData']/text()"))
    js_list = json.loads(j, encoding='utf8')
    # js_list = eval(j)['pageData']['storeLocatorDirectoryModel']['storeDirectory']['storeLocatorFacetGroupModels']
    return js_list['pageData']['storeLocatorDirectoryModel']['storeDirectory']['storeLocatorFacetGroupModels']


def fetch_data():
    out = []
    url = 'https://www.rei.com/map/store'
    js_list = get_json(url)

    for js in js_list:
        states = js.get('storeLocatorStateFacetModels')
        for state in states:
            data = state.get('storeLocatorDataQueryModelList')
            for d in data:
                j = d.get('storeDataModel')
                locator_domain = url
                page_url = url
                location_name = j.get('storeName')
                street_address = j.get('address1') or '<MISSING>'
                city = j.get('city') or '<MISSING>'
                state = j.get('stateCode') or '<MISSING>'
                postal = j.get('zip') or '<MISSING>'
                country_code = j.get('countryCode') or '<MISSING>'
                store_number = j.get('storeNumber') or '<MISSING>'
                phone = j.get('phoneNumber') or '<MISSING>'
                latitude = j.get('latitude') or '<MISSING>'
                longitude = j.get('longitude') or '<MISSING>'
                location_type = j.get('Type', '<MISSING>')

                hours = j.get('storeHours')
                _tmp = []
                for h in hours:
                    day = h.get('days')
                    start = h.get('openAt')
                    end = h.get('closeAt')
                    _tmp.append(f'{day}  {start} - {end}')

                hours_of_operation = ';'.join(_tmp) or '<MISSING>'

                row = [locator_domain, page_url, location_name, street_address, city, state, postal,
                       country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
