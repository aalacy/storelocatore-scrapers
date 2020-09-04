import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "office_name", "building_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.uscourts.gov/fedcf-query?query={%22by%22:%22location%22,%22page%22:0,%22description%22:%22USA%22,%22county%22:%22%22,%22state%22:%22%22,%22zip%22:%22%22,%22country%22:%22US%22,%22locationType%22:%22state%22,%22lat%22:46.7300153,%22lng%22:-94.68297629999999,%22filters%22:%22default%22}'
    r = session.get(url, headers=headers)
    website = 'uscourts.gov'
    country = 'US'
    for item in json.loads(r.content)['results']['locations']:
        typ = item['CourtType'].replace('\\','')
        store = item['LocationId']
        loc = 'https://www.uscourts.gov/federal-court-finder/location/' + store
        office_name = item['OfficeName']
        add = item['BuildingAddress']
        city = item['BuildingCity']
        state = item['BuildingState']
        zc = item['BuildingZip']
        phone = item['Phone']
        hours = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        building_name = item['BuildingName']
        if building_name == '':
            building_name = '<MISSING>'
            name = office_name
        else:
            name = office_name.split(' - ')[0] + ' ' + building_name
        if typ == '':
            typ = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, loc, name, office_name, building_name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
