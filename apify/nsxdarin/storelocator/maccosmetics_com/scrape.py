import csv
import requests
import time
import random

from helpers import printRequestInfo, getFormattedDateTime, setCookie

session = requests.Session()

headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,la;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}

def get_locations_page(): 
  url = 'https://www.maccosmetics.com/stores'
  r = session.get(url, headers=headers)
  if r.encoding is None: r.encoding = 'utf-8'

def setup_for_posts():
  setCookie(session, 'www.maccosmetics.com', 'has_js', '1')
  setCookie(session, '.maccosmetics.com', 'client.isMobile', '0')
  setCookie(session, None, 'OptanonConsent', 'isIABGlobal=false&datestamp=' + getFormattedDateTime() +
            '+GMT-0400+(Eastern+Daylight+Time)&version=5.5.0&landingPath=https%3A%2F%2Fwww.maccosmetics.com%2Fstores')
  setCookie(session, 'www.maccosmetics.com', 'MP_CONFIG',
            '%7B%22language_id%22%3A48%2C%22country_id%22%3A1%7D')
  setCookie(session, '.maccosmetics.com', 'AKA_A2', 'A')

  headers['origin'] = 'https://www.maccosmetics.com'
  headers['referer'] = 'https: // www.maccosmetics.com/stores'
  headers['sec-fetch-dest'] = 'empty'
  headers['sec-fetch-mode'] = 'cors'
  headers['sec-fetch-site'] = 'same-origin'
  headers['x-requested-with'] = 'XMLHttpRequest'


def init_session(): 

  # if __debug__:
    # print('Posting to https://www.maccosmetics.com/static/751a18e8ae4197a37d96984c95bb902')

  headers['content-type'] = 'text/plain;charset=UTF-8'

  data = '{"sensor_data":"7a74G7m23Vrp0o5c9157751.54-1,2,-94,-100,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36,uaend,12147,20030107,en-US,Gecko,3,0,0,0,390235,8144734,1920,1057,1920,1080,970,946,1920,,cpen:0,i1:0,dm:0,cwen:0,non:1,opc:0,fc:0,sc:0,wrc:1,isc:0,vib:1,bat:1,x11:0,x12:1,8984,0.0108206025,793009072367,loc:-1,2,-94,-101,do_en,dm_en,t_en-1,2,-94,-105,0,-1,0,1,2843,973,0;1,-1,0,1,2497,627,0;0,0,0,0,630,630,0;0,-1,0,1,4148,1215,0;0,-1,0,1,3925,992,0;0,0,0,0,630,630,0;0,-1,0,0,-1,-1,0;-1,2,-94,-102,0,-1,0,1,2843,973,0;1,-1,0,1,2497,627,0;0,0,0,0,630,630,0;0,-1,0,1,4148,1215,0;0,-1,0,1,3925,992,0;0,0,0,0,630,630,0;0,-1,0,0,-1,-1,0;-1,2,-94,-108,-1,2,-94,-110,-1,2,-94,-117,-1,2,-94,-111,-1,2,-94,-109,-1,2,-94,-114,-1,2,-94,-103,-1,2,-94,-112,https://www.maccosmetics.com/stores-1,2,-94,-115,1,32,32,0,0,0,0,2,0,1586018144734,-999999,16966,0,0,2827,0,0,5,0,0,AD54B6A55AA42D546164945727B002EF~-1~YAAQlo1AF+pB4RpxAQAAg0gMRgOFmeAsNgQ9mclJetCwC0laqi9uVJE/jyuDdi4wtzP5Ul58+fqnX04OFDmtUIC8xj1yHsH0Us2yPMFh+Ur/1BUvXw1+PLIy4rOfa3x/7csetEfpmMUYog72SeJKN02Tbvs7oxSPSsUq+2aSxJZvK9GhqZdMzAlpfgixWVwFI18jW0ZgVmlKbJIEBWoJx6mzCNyyNa+h6yzzNQr3l7YdnruomDflHzr7nhOqe/Ovrq31phIp3IvZPzk80rb3LhHKlmzhPN/o3U91GR2eV0ksiZ6+syA5zxnGGjoA/Qnm~-1~-1~-1,30681,-1,-1,30261693-1,2,-94,-106,0,0-1,2,-94,-119,-1-1,2,-94,-122,0,0,0,0,1,0,0-1,2,-94,-123,-1,2,-94,-124,-1,2,-94,-126,-1,2,-94,-127,-1,2,-94,-70,-1-1,2,-94,-80,94-1,2,-94,-116,1018091450-1,2,-94,-118,89722-1,2,-94,-121,;6;-1;0"}'
  
  r = session.post('https://www.maccosmetics.com/static/751a18e8ae4197a37d96984c95bb902', headers=headers, data=data)
  if r.encoding is None: r.encoding = 'utf-8'
  
def get_csrf_token(): 
  headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

  r = session.post('https://www.maccosmetics.com/rpc/jsonrpc.tmpl?dbgmethod=csrf.getToken', headers=headers, data="JSONRPC=%5B%7B%22method%22%3A%22csrf.getToken%22%2C%22id%22%3A1%2C%22params%22%3A%5B%7B%7D%5D%7D%5D")
  if r.encoding is None: r.encoding = 'utf-8'

def get_locations_data(): 
  url = 'https://www.maccosmetics.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents'
  payload = {'JSONRPC': '[{"method":"locator.doorsandevents","id":3,"params":[{"fields":"DOOR_ID, DOORNAME, EVENT_NAME, SUB_HEADING, EVENT_START_DATE, EVENT_END_DATE, EVENT_IMAGE, EVENT_FEATURES, EVENT_TIMES, SERVICES, STORE_HOURS, ADDRESS, ADDRESS2, STATE_OR_PROVINCE, CITY, REGION, COUNTRY, ZIP_OR_POSTAL, PHONE1, PHONE2, STORE_TYPE, LONGITUDE, LATITUDE, COMMENTS","country":"United States","latitude":44.9951298,"longitude":-93.4352207,"uom":"mile","radius":15000,"region_id":"0,47,27"}]}]'
             }
  r = session.post(url, headers=headers, data=payload)
  if r.encoding is None: r.encoding = 'utf-8'
  return r


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    get_locations_page()
    time.sleep(random.random()*5)
    setup_for_posts()
    init_session()
    time.sleep(random.random()*5)
    get_csrf_token()
    time.sleep(random.random()*5)
    r = get_locations_data()
    for line in r.iter_lines(decode_unicode=True):
        if '"DOOR_ID":' in line:
            items = line.split('"DOOR_ID":')
            for item in items:
                if '"STORE_TYPE":"' in item:
                    loc = '<MISSING>'
                    typ = item.split('"STORE_TYPE":"')[1].split('"')[0]
                    store = item.split(',')[0]
                    website = 'maccosmetics.com'
                    hours = ''
                    city = item.split('"CITY":"')[1].split('"')[0]
                    country = item.split('"COUNTRY":"')[1].split('"')[0]
                    if 'United States' in country:
                        country = 'US'
                    if 'Canada' in country:
                        country = 'CA'
                    name = item.split('"DOORNAME":"')[1].split('"')[0] + ' ' + item.split('SUB_HEADING":"')[1].split('"')[0]
                    name = name.strip()
                    phone = item.split('"PHONE1":"')[1].split('"')[0]
                    lat = item.split('"LATITUDE":"')[1].split('"')[0]
                    lng = item.split('"LONGITUDE":"')[1].split('"')[0]
                    add = item.split('"ADDRESS":"')[1].split('"')[0] + ' ' + item.split('"ADDRESS2":"')[1].split('"')[0]
                    add = add.strip()
                    zc = item.split('"ZIP_OR_POSTAL":"')[1].split('"')[0]
                    state = item.split('"STATE_OR_PROVINCE":"')[1].split('"')[0]
                    if 'STORE_HOURS":""' in item:
                        hours = ''
                    else:
                        days = item.split('"STORE_HOURS":[')[1].split(']')[0].split('"hours":"')
                        for day in days:
                            if '"day":"' in day:
                                dname = day.split('"day":"')[1].split('"')[0]
                                hrs = dname + ': ' + day.split('"')[0]
                                if hours == '':
                                    hours = hrs
                                else:
                                    hours = hours + '; ' + hrs
                    if hours == '':
                        hours = '<MISSING>'
                    if typ == '':
                        typ = 'Dept Store'
                    if phone == '':
                        phone = '<MISSING>'
                    if state == '' or state == '.':
                        state = '<MISSING>'
                    if zc == '':
                        zc = '<MISSING>'
                    if country == 'US':
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
