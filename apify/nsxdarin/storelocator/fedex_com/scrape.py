import csv
import urllib2
import requests
import json

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    res = 50000
    coords = ['45.0,-93.5']
    for coord in coords:
        x = coord.split(',')[0]
        y = coord.split(',')[1]
        url = 'https://6-dot-fedexlocationstaging-1076.appspot.com/rest/search/stores?&where=ST_DISTANCE(geometry%2C+ST_POINT(' + y + '%2C+' + x + '))%3C160900000&version=published&key=AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE&clientId=WDRP&service=list&select=geometry%2C+LOC_ID%2C+PROMOTION_ID%2C+SEQUENCE_ID%2CST_DISTANCE(geometry%2C+ST_POINT(' + y + '%2C+' + x + '))as+distance&orderBy=distance+ASC&limit=' + str(res) + '&maxResults=' + str(res)
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if 'LOC_ID' in line:
                items = line.split('{"LOC_ID":"')
                for item in items:
                    if '{"features":' not in item:
                        lid = item.split('"')[0]
                        if lid not in locs:
                            locs.append(lid)
    print('%s Locations Found...' % str(len(locs)))
    for loc in locs:
        print('Pulling Location %s...' % loc)
        lurl = 'https://6-dot-fedexlocationstaging-1076.appspot.com/rest/search/stores?&version=published&key=AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE&clientId=WDRP&service=detail%7CLOC_ID%3D%27' + loc + '%27'
        r2 = session.get(lurl, headers=headers)
        array = json.loads(r2.content.split('"properties":')[1].split('}]')[0])
        lat = r2.content.split('"coordinates":[')[1].split(',')[0]
        lng = r2.content.split('"coordinates":[')[1].split(',')[1].split(']')[0]
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
        country = 'US'
        typ = array['LOC_SUB_TYPE']
        store = loc
        if phone == '':
            phone = '<MISSING>'
        if typ == '':
            typ = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
