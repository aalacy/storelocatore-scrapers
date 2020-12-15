from sgrequests import SgRequests
import csv

base_url = 'https://www.sleepcountry.ca/'
def fetch_data():
    url = 'https://www.sleepcountry.ca/ccstorex/custom/v1/stores/?locale=en'
    json_data = SgRequests().get(url).json()
    addresses = []
    for val in json_data['result']:
        store = []
        store.append(base_url)
        store.append(val['name'] if val['name'] else '<MISSING>')
        store.append(val['address1'] if val['address1'] else '<MISSING>')
        store.append(val['city'] if val['city'] else '<MISSING>')
        store.append(val['stateAddress'] if val['stateAddress'] else '<MISSING>')
        store.append(val['postalCode'] if val['postalCode'] else '<MISSING>')
        store.append(val['country'] if val['country'] else '<MISSING>')
        store.append('<MISSING>')
        store.append(val['phoneNumber'] if val['phoneNumber'] else '<MISSING>')
        store.append('<MISSING>')
        store.append(val['latitude'] if val['latitude'] else '<MISSING>')
        store.append(val['longitude'] if val['longitude'] else '<MISSING>')
        store.append(val['hours'].replace('<table>','').replace('<tr>','').replace('\n','').replace('<th>','').replace('</th>','').replace('</tr>','').replace('</table>','').replace('<td>','').replace('</td>','') if val['hours'] else '<MISSING>')
        store.append('https://www.sleepcountry.ca/storelocator')
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def load_data(data):
    with open('data.csv', mode='w', encoding="utf-8",newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)



def scrape():
    data = fetch_data()
    load_data(data)

if __name__ == '__main__':
    scrape()
