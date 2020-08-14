import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://mothersnc.com/wp-admin/admin-ajax.php?action=store_search&lat=38.1030032&lng=-118.4104684&max_results=100&search_radius=500'
    r = session.get(url, headers=headers)
    website = 'mothersnutritionalcenter.com'
    typ = '<MISSING>'
    country = 'US'
    items = json.loads(r.content)
    for item in items:
        loc = item['permalink'].replace('\\','')
        name = item['store']
        add = item['address']
        store = item['id']
        city = item['city']
        state = item['state']
        zc = item['zip']
        lat = item['lat']
        lng = item['lng']
        phone = item['phone']
        hours = item['hours']
        try:
            hours = hours.replace('<\/td><td><time>',': ').replace('<\/time><\/td><\/tr><tr><td>','; ')
            hours = hours.split('wpsl-opening-hours')[1].split('<td>',1)[1].split('<\/td><\/tr><\/table>')[0]
        except:
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
