import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('baskinrobbins_ca')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'http://cdn.storelocatorwidgets.com/json/4a009290a87670e408c8d77aada5c556?callback=slw&_=1573064176270'
    r = session.get(url, headers=headers)
    items = r.text.split('"storeid":"')
    for item in items:
        if '"name":"' in item and 'slw({"settings":' not in item:
            item = item.replace(', Canada",','",')
            item = item.replace(', Canada\\r\\n",','",')
            item = item.replace(', CA",','",')
            item = item.replace(', British Columbia, ',', BC ')
            item = item.replace('Ontario\\r\\n','ON ')
            store = item.split('"')[0]
            name = item.split('"name":"')[1].split('"')[0]
            try:
                addinfo = item.split('"address":"')[1].split('"')[0].replace('\\r\\n',',')
            except:
                addinfo = item.split('"name":"')[1].split('"')[0]
            website = 'baskinrobbins.ca'
            typ = 'Store'
            try:
                phone = item.split('"phone":"')[1].split('"')[0]
            except:
                phone = '<MISSING>'
            try:
                lat = item.split('"map_lat":"')[1].split('"')[0]
                lng = item.split('"map_lng":"')[1].split('"')[0]
            except:
                lat = '<MISSING>'
                lng = '<MISSING>'
            country = 'CA'
            if addinfo.count(',') == 3:
                add = addinfo.split(',',1)[0].strip()
            else:
                add = addinfo.split(',')[0].strip()
            #logger.info(addinfo)
            try:
                zc = addinfo.rsplit(',',1)[1].strip().split(' ',1)[1]
            except:
                zc = '<MISSING>'
            try:
                state = addinfo.rsplit(',',1)[1].strip().split(' ',1)[0]
            except:
                state = '<MISSING>'
            try:
                city = addinfo.rsplit(',',2)[1].strip()
            except:
                city = '<MISSING>'
            try:
                hours = 'Mon: ' + item.split('"hours_Monday":"')[1].split('"')[0]
                hours = hours + '; Tue: ' + item.split('"hours_Tuesday":"')[1].split('"')[0]
                hours = hours + '; Wed: ' + item.split('"hours_Wednesday":"')[1].split('"')[0]
                hours = hours + '; Thu: ' + item.split('"hours_Thursday":"')[1].split('"')[0]
                hours = hours + '; Fri: ' + item.split('"hours_Friday":"')[1].split('"')[0]
                hours = hours + '; Sat: ' + item.split('"hours_Saturday":"')[1].split('"')[0]
                hours = hours + '; Sun: ' + item.split('"hours_Sunday":"')[1].split('"')[0]
            except:
                hours = '<MISSING>'
            if city == 'ON':
                zc = state + ' ' + zc
                state = 'ON'
                city = addinfo.split(',')[2].strip()
            if city == 'Canada':
                zc = state + ' ' + zc
                state = 'ON'
                city = 'Milton'
            if city == 'BC V7P':
                zc = 'BC V7P'
                state = 'BC'
                city = 'North Vancouver'
            if add == 'Tsawassen Mills Mall':
                add = '5000 Canoe Pass Way'
                city = 'Delta'
                state = 'BC'
                zc = '<MISSING>'
            if add == '1660 Upper James Street':
                city = 'Hamilton'
            if add == '3450 Dundas Street Unit B-2B':
                city = 'Burlington'
            if add == '15 Westney Road North Unit 11-A':
                city = 'Ajax'
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
