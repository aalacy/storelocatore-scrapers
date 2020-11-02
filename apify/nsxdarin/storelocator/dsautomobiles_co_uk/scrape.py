import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

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
    url = 'https://www.dsautomobiles.co.uk/_/Layout_DSPP_DealerLocator/getStoreList?lat=51.51&long=-0.13&page=15041&version=58&order=2&area=50000&ztid=&attribut=&brandactivity=DS'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '{"id":"' in line:
            items = line.split('{"id":"')
            for item in items:
                if ',"name":"' in item:
                    name = item.split(',"name":"')[1].split('"')[0]
                    website = 'dsautomobiles.co.uk'
                    typ = '<MISSING>'
                    country = 'GB'
                    hours = ''
                    addinfo = item.split('"address":"')[1].split('"')[0]
                    add = addinfo.split('<br')[0]
                    city = addinfo.rsplit('&nbsp;',1)[1]
                    state = '<MISSING>'
                    zc = addinfo.split('<br \\/>')[1].split('&')[0]
                    phone = item.split(',"phone":"')[1].split('"')[0]
                    store = item.split('"')[0]
                    try:
                        stub = item.split('review.dsautomobiles.co.uk\\/en\\/')[1].split('\\')[0]
                    except:
                        stub = ''
                    if stub == '':
                        loc = '<MISSING>'
                    else:
                        loc = 'https://dealer.dsautomobiles.co.uk/' + stub
                    lat = item.split('"lat":')[1].split(',')[0]
                    lng = item.split('"lng":')[1].split(',')[0]
                    add = add.replace('&nbsp;-','').replace('&nbsp;',' ').replace('\\/','/')
                    durl = 'https://www.dsautomobiles.co.uk/_/Layout_DSPP_DealerLocator/getDealer?id=' + store
                    r2 = session.get(durl, headers=headers)
                    if r2.encoding is None: r2.encoding = 'utf-8'
                    for line2 in r2.iter_lines(decode_unicode=True):
                        if '"timetable":"' in line2:
                            hours = line2.split('"timetable":"')[1].replace('<br \\/>",','"').split('"')[0].replace('<br \\/>','; ')
                        if hours == '':
                            hours = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
