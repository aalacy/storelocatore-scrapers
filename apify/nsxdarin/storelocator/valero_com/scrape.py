import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
           'cookie': 'ASP.NET_SessionId=pvspsettljlu12yl2gr5oskr; BIGipServervaleromaps.valero.com_pool=723637002.47873.0000; TS01f7c95b=01353f239a3013bee49c7bdc49f403c0576db09e8dd05a3e33f149c4cf7959ae8e6567dfd20e63fac38c2f3282c7df909b7f9c707282c3f749a1b61c796b94644192db4aa958f4d8fd0839ef7c3f2b0f7728dc5e76; WT_FPC=id=10.211.46.226-1459936176.30801219:lv=1584545799435:ss=1584545768052'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    url = 'https://valeromaps.valero.com/Home/Search?SPHostUrl=https%3A%2F%2Fwww.valero.com%2Fen-us'
    for x in range(15, 50, 5):
        for y in range(-65, -120, -5):
            print('%s-%s...' % (str(x), str(y)))
            nelat = float(x) + 5
            swlat = float(x) - 5
            nelng = float(y) + 5
            swlng = float(y) - 5
            print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
            payload = {'NEBound_Lat': str(nelat),
                       'NEBound_Long': str(nelng),
                       'SWBound_Lat': str(swlat),
                       'SWBound_Long': str(swlng),
                       'center_Lat': x,
                       'center_Long': y
                       }
            r = session.post(url, headers=headers, data=payload)
            for line in r.iter_lines():
                if 'UniqueID":"' in line:
                    items = line.split('UniqueID":"')
                    print(len(items))
                    for item in items:
                        if '"DetailName":"' in item:
                            name = item.split('"StationName":"')[1].split('"')[0]
                            phone = item.split('Phone":"')[1].split('"')[0].strip().replace('\t','')
                            lat = item.split('Latitude":')[1].split(',')[0]
                            lng = item.split(',"Longitude":')[1].split(',')[0]
                            store = item.split('"')[0]
                            website = 'valero.com'
                            loc = '<MISSING>'
                            typ = '<MISSING>'
                            addinfo = item.split('"Address":"')[1].split('"')[0]
                            zc = addinfo.rsplit(' ',1)[1]
                            add = addinfo.split(',')[0]
                            city = '<MISSING>'
                            state = addinfo.split(',')[1].strip().split(' ')[0]
                            hours = '<MISSING>'
                            country = 'US'
                            if phone == '':
                                phone = '<MISSING>'
                            if store not in ids:
                                ids.append(store)
                                print('Pulling Store ID #%s...' % store)
                                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
