import csv
from sgrequests import SgHttpClient
import json

client = SgHttpClient('6-dot-fedexlocationstaging-1076.appspot.com')

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        'Connection':'Keep-Alive'
}

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    usa = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    canada = ['NF','NS','PE','NB','SK','ON','QC','PQ','YK','NT','NU','AB']
    paths = ['/rest/search/stores?&projectId=13284125696592996852&where=ST_DISTANCE(geometry%2C+ST_POINT(-73.9859414%2C+40.7135097))%3C1609000&version=published&key=AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE&clientId=WDRP&service=list&select=geometry%2C+LOC_ID%2C+PROMOTION_ID%2C+SEQUENCE_ID%2CST_DISTANCE(geometry%2C+ST_POINT(-73.9859414%2C+40.7135097))as+distance&orderBy=distance+ASC&limit=100000&maxResults=100000&_=1566253089266', '/rest/search/stores?&projectId=13284125696592996852&where=ST_DISTANCE(geometry%2C+ST_POINT(-120.9859414%2C+40.7135097))%3C1609000&version=published&key=AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE&clientId=WDRP&service=list&select=geometry%2C+LOC_ID%2C+PROMOTION_ID%2C+SEQUENCE_ID%2CST_DISTANCE(geometry%2C+ST_POINT(-73.9859414%2C+40.7135097))as+distance&orderBy=distance+ASC&limit=100000&maxResults=100000&_=1566253089266', '/rest/search/stores?&projectId=13284125696592996852&where=ST_DISTANCE(geometry%2C+ST_POINT(-157.9859414%2C+20.7135097))%3C1609000&version=published&key=AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE&clientId=WDRP&service=list&select=geometry%2C+LOC_ID%2C+PROMOTION_ID%2C+SEQUENCE_ID%2CST_DISTANCE(geometry%2C+ST_POINT(-73.9859414%2C+40.7135097))as+distance&orderBy=distance+ASC&limit=100000&maxResults=100000&_=1566253089266', '/rest/search/stores?&projectId=13284125696592996852&where=ST_DISTANCE(geometry%2C+ST_POINT(-105.9859414%2C+40.7135097))%3C1609000&version=published&key=AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE&clientId=WDRP&service=list&select=geometry%2C+LOC_ID%2C+PROMOTION_ID%2C+SEQUENCE_ID%2CST_DISTANCE(geometry%2C+ST_POINT(-73.9859414%2C+40.7135097))as+distance&orderBy=distance+ASC&limit=100000&maxResults=100000&_=1566253089266', '/rest/search/stores?&projectId=13284125696592996852&where=ST_DISTANCE(geometry%2C+ST_POINT(-157.9859414%2C+55.7135097))%3C1609000&version=published&key=AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE&clientId=WDRP&service=list&select=geometry%2C+LOC_ID%2C+PROMOTION_ID%2C+SEQUENCE_ID%2CST_DISTANCE(geometry%2C+ST_POINT(-73.9859414%2C+40.7135097))as+distance&orderBy=distance+ASC&limit=100000&maxResults=100000&_=1566253089266']
    locs = set()
    for path in paths:
        data = json.loads(client.get(path, headers=headers).decode("utf-8"))
        for feature in data['features']:
            loc_id = feature['properties']['LOC_ID']
            locs.add(loc_id)

    print('%s Locations Found...' % str(len(locs)))

    i = 0
    for loc in locs:
        i += 1
        lpath = '/rest/search/stores?&version=published&key=AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE&clientId=WDRP&service=detail%7CLOC_ID%3D%27' + loc + '%27'
        r2 = json.loads(client.get(lpath, headers=headers).decode('utf-8'))['features'][0]
        array = r2['properties']
        lat = r2['geometry']["coordinates"][1]
        lng = r2['geometry']["coordinates"][0]
        website = 'fedex.com'
        name = array['ENG_DISPLAY_NAME']
        add = array['ENG_ADDR_LINE_1']
        city = array['ENG_CITY_NAME']
        state = array['STATE_CODE']
        zc = array['POSTAL_CODE']
        phone = array['PHONE_NBR']
        hours = 'Mon: ' + array['MON_BUS_HRS_1_OPEN_TIME'] + '-' + array['MON_BUS_HRS_1_CLOSE_TIME']
        hours = hours + '; Tue: ' + array['TUE_BUS_HRS_1_OPEN_TIME'] + '-' + array['TUE_BUS_HRS_1_CLOSE_TIME']
        hours = hours + '; Wed: ' + array['WED_BUS_HRS_1_OPEN_TIME'] + '-' + array['WED_BUS_HRS_1_CLOSE_TIME']
        hours = hours + '; Thu: ' + array['THU_BUS_HRS_1_OPEN_TIME'] + '-' + array['THU_BUS_HRS_1_CLOSE_TIME']
        hours = hours + '; Fri: ' + array['FRI_BUS_HRS_1_OPEN_TIME'] + '-' + array['FRI_BUS_HRS_1_CLOSE_TIME']
        hours = hours + '; Sat: ' + array['SAT_BUS_HRS_1_OPEN_TIME'] + '-' + array['SAT_BUS_HRS_1_CLOSE_TIME']
        hours = hours + '; Sun: ' + array['SUN_BUS_HRS_1_OPEN_TIME'] + '-' + array['SUN_BUS_HRS_1_CLOSE_TIME']
        if '0' not in hours:
            hours = '<MISSING>'
        country = ''
        typ = array['LOC_SUB_TYPE']
        store = loc
        if phone == '':
            phone = '<MISSING>'
        if typ == '':
            typ = '<MISSING>'
        if state == '':
            state = '<MISSING>'
        if state in canada:
            country = 'CA'
        if state in usa:
            country = 'US'
        if country == 'US' or country == 'CA':
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
