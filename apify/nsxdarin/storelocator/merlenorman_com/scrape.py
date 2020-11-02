import json
import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'x-requested-with': 'XMLHttpRequest',
           'cookie': 'Authsite=httpss%3A%2F%2Fwww.merlenorman.com%2Fstores; AppKey=NONE; W2GISM=0a7228e262eabb07107d610814d42f8f'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    ids = []
    url = 'https://hosted.where2getit.com/merlenorman/rest/locatorsearch?like=0.5255049170991888'
    payload = {"request":{"appkey":"3FC04602-C261-11DD-B20A-854637ABAA09",
                          "formdata":{"geoip":"false","dataview":"store_default","limit":2500,
                                      "geolocs":{"geoloc":[{"addressline":"Kansas City, MO","country":"","latitude":"","longitude":""}]},
                                      "order":"rank, _distance","searchradius":"5000",
                                      "where":{"or":{"retail":{"eq":""},"outlet":{"eq":""},"factory":{"eq":""},"promo":{"eq":""}}},"false":"0"}}}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for item in json.loads(r.content)['response']['collection']:
        website = 'merlenorman.com'
        typ = '<MISSING>'
        state = item['state']
        prov = item['province']
        name = item['name']
        country = item['country']
        lng = item['longitude']
        lat = item['latitude']
        try:
            loc = item['url'].replace(' target=_new','')
        except:
            loc = '<MISSING>'
        store = item['clientkey']
        add = item['address1']
        try:
            add = add + ' ' + item['address2']
        except:
            pass
        city = item['city']
        zc = item['postalcode']
        phone = item['phone']
        try:
            hours = 'Mon: ' + item['monday']
            hours = hours + '; Tue:' + item['tuesday']
            hours = hours + '; Wed:' + item['wednesday']
            hours = hours + '; Thu:' + item['thursday']
            hours = hours + '; Fri:' + item['friday']
            hours = hours + '; Sat:' + item['saturday']
            hours = hours + '; Sun:' + item['sunday']
        except:
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if store == '':
            store = '<MISSING>'
        if state is None:
            state = prov
        if store not in ids:
            ids.append(store)
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    payload = {"request":{"appkey":"3FC04602-C261-11DD-B20A-854637ABAA09",
                          "formdata":{"geoip":"false","dataview":"store_default","limit":2500,
                                      "geolocs":{"geoloc":[{"addressline":"New York, NY","country":"","latitude":"","longitude":""}]},
                                      "order":"rank, _distance","searchradius":"5000",
                                      "where":{"or":{"retail":{"eq":""},"outlet":{"eq":""},"factory":{"eq":""},"promo":{"eq":""}}},"false":"0"}}}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for item in json.loads(r.content)['response']['collection']:
        website = 'merlenorman.com'
        typ = '<MISSING>'
        state = item['state']
        prov = item['province']
        name = item['name']
        country = item['country']
        lng = item['longitude']
        lat = item['latitude']
        try:
            loc = item['url'].replace(' target=_new','')
        except:
            loc = '<MISSING>'
        store = item['clientkey']
        add = item['address1']
        try:
            add = add + ' ' + item['address2']
        except:
            pass
        city = item['city']
        zc = item['postalcode']
        phone = item['phone']
        try:
            hours = 'Mon: ' + item['monday']
            hours = hours + '; Tue:' + item['tuesday']
            hours = hours + '; Wed:' + item['wednesday']
            hours = hours + '; Thu:' + item['thursday']
            hours = hours + '; Fri:' + item['friday']
            hours = hours + '; Sat:' + item['saturday']
            hours = hours + '; Sun:' + item['sunday']
        except:
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if store == '':
            store = '<MISSING>'
        if state is None:
            state = prov
        if store not in ids:
            ids.append(store)
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    payload = {"request":{"appkey":"3FC04602-C261-11DD-B20A-854637ABAA09",
                          "formdata":{"geoip":"false","dataview":"store_default","limit":2500,
                                      "geolocs":{"geoloc":[{"addressline":"Seattle, WA","country":"","latitude":"","longitude":""}]},
                                      "order":"rank, _distance","searchradius":"5000",
                                      "where":{"or":{"retail":{"eq":""},"outlet":{"eq":""},"factory":{"eq":""},"promo":{"eq":""}}},"false":"0"}}}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for item in json.loads(r.content)['response']['collection']:
        website = 'merlenorman.com'
        typ = '<MISSING>'
        state = item['state']
        prov = item['province']
        name = item['name']
        country = item['country']
        lng = item['longitude']
        lat = item['latitude']
        try:
            loc = item['url'].replace(' target=_new','')
        except:
            loc = '<MISSING>'
        store = item['clientkey']
        add = item['address1']
        try:
            add = add + ' ' + item['address2']
        except:
            pass
        city = item['city']
        zc = item['postalcode']
        phone = item['phone']
        try:
            hours = 'Mon: ' + item['monday']
            hours = hours + '; Tue:' + item['tuesday']
            hours = hours + '; Wed:' + item['wednesday']
            hours = hours + '; Thu:' + item['thursday']
            hours = hours + '; Fri:' + item['friday']
            hours = hours + '; Sat:' + item['saturday']
            hours = hours + '; Sun:' + item['sunday']
        except:
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if store == '':
            store = '<MISSING>'
        if state is None:
            state = prov
        if store not in ids:
            ids.append(store)
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
