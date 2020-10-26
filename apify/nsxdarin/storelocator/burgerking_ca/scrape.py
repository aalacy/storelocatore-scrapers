import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.bk.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<loc>' in line:
            items = line.split('<loc>')
            for item in items:
                if '--british-columbia--' in item or '--saskatchewan--' in item or '--alberta--' in item or '--ontario--' in item or '--prince-edward--' in item or '--quebec--' in item or '--new-brunswick--' in item or '--newfoundland/' in item or '--nova-scotia--' in item or '--manitoba--' in item:
                    locs.append(item.split('<')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        store = loc.split('/store/')[1].split('/')[0]
        lurl = 'https://czqk28jt.apicdn.sanity.io/v1/data/query/prod_bk_us?query=*%5B%20_type%20%3D%3D%20%27restaurant%27%20%26%26%20number%20%3D%3D%20%24storeNumber%20%5D%20%7B_id%2CdeliveryHours%2CdiningRoomHours%2CcurbsideHours%2CdrinkStationType%2CdriveThruHours%2CdriveThruLaneType%2Cemail%2CfranchiseGroupId%2CfranchiseGroupName%2CfrontCounterClosed%2ChasBreakfast%2ChasBurgersForBreakfast%2ChasCurbside%2ChasDineIn%2ChasCatering%2ChasDelivery%2ChasDriveThru%2ChasMobileOrdering%2ChasParking%2ChasPlayground%2ChasTakeOut%2ChasWifi%2Clatitude%2Clongitude%2CmobileOrderingStatus%2Cname%2Cnumber%2CparkingType%2CphoneNumber%2CphysicalAddress%2CplaygroundType%2Cpos%2CposRestaurantId%2CrestaurantPosData-%3E%7B_id%2C%20lastHeartbeatTimestamp%2C%20heartbeatStatus%2C%20heartbeatOverride%7D%2Cstatus%2CrestaurantImage%7B...%2C%20asset-%3E%7D%7D&%24storeNumber=%22' + store + '%22'
        r2 = session.get(lurl, headers=headers)
        website = 'burgerking.ca'
        typ = 'Restaurant'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'CA'
        phone = ''
        lat = ''
        lng = ''
        hours = ''
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if ',"name":"' in line2:
                name = line2.split(',"name":"')[1].split('"')[0]
                add = line2.split('"address1":"')[1].split('"')[0] + ' ' + line2.split('"address2":"')[1].split('"')[0]
                add = add.strip()
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"stateProvinceShort":"')[1].split('"')[0]
                phone = line2.split('"phoneNumber":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(',')[0]
                lng = line2.split('"longitude":')[1].split(',')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                line2 = line2.replace('23:59:59','00:00:00')
                try:
                    hours = 'Mon: ' + line2.split('"monOpen":"')[1].split(':00"')[0].split(' ')[1] + '-' + line2.split('"monClose":"')[1].split(':00"')[0].split(' ')[1]
                    hours = hours + '; ' + 'Tue: ' + line2.split('"tueOpen":"')[1].split(':00"')[0].split(' ')[1] + '-' + line2.split('"tueClose":"')[1].split(':00"')[0].split(' ')[1]
                    hours = hours + '; ' + 'Wed: ' + line2.split('"wedOpen":"')[1].split(':00"')[0].split(' ')[1] + '-' + line2.split('"wedClose":"')[1].split(':00"')[0].split(' ')[1]
                    hours = hours + '; ' + 'Thu: ' + line2.split('"thrOpen":"')[1].split(':00"')[0].split(' ')[1] + '-' + line2.split('"thrClose":"')[1].split(':00"')[0].split(' ')[1]
                    hours = hours + '; ' + 'Fri: ' + line2.split('"friOpen":"')[1].split(':00"')[0].split(' ')[1] + '-' + line2.split('"friClose":"')[1].split(':00"')[0].split(' ')[1]
                    hours = hours + '; ' + 'Sat: ' + line2.split('"satOpen":"')[1].split(':00"')[0].split(' ')[1] + '-' + line2.split('"satClose":"')[1].split(':00"')[0].split(' ')[1]
                    hours = hours + '; ' + 'Sun: ' + line2.split('"sunOpen":"')[1].split(':00"')[0].split(' ')[1] + '-' + line2.split('"sunClose":"')[1].split(':00"')[0].split(' ')[1]
                except:
                    hours = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                if city == '':
                    if ',' in add:
                        city = add.split(',')[1].strip()
                    else:
                        city = '<MISSING>'
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
