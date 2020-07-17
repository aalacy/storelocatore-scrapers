import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json;charset=UTF-8',
           'accept': 'application/json, text/plain, */*'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def post(url, headers, data, attempts=1): 
    global session
    if attempts == 10:
        print(f'could not post after {attempts} tries, giving up')
        raise SystemExit
    try: 
        r = session.post(url, headers=headers, data=data)
        return r
    except Exception as ex:
        print(f'exception getting {url}: {ex}')
        session = SgRequests() 
        return post(url, headers, data, attempts+1)


def fetch_data():
    locs = []
    # print('Alaska')
    locstr = 'Anchorage, AK'
    payload = {"searchType":"Location",
               "searchValue":locstr,
               "boxSearchCollection":[{"lat1":0,"long1":0,"lat2":0,"long2":0,
                                       "boxes":[]}],"filters":[],
               "hasSales":False,
               "hasService":False,
               "hasParts":False,
               "distance":1000000,
               "clientTime":"2020-07-01 10:30:37",
               "country":"USA",
               "brand":"INT",
               "sort":"nearToFar",
               "isDiamondEdge":False,
               "isLoves":False,
               "isSpeedCo":False}
    url = 'https://dealerlocator-api.internationaltrucks.com/api/v1/dealers/getdealers/'
    r = post(url, headers=headers, data=json.dumps(payload))
    website = 'internationaltrucks.com'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"FullAccountNumber":"' in line:
            items = line.split('{"FullAccountNumber":"')
            for item in items:
                if '"StateProvince":"' in item:
                    store = item.split('"')[0]
                    name = item.split('"AccountName":"')[1].split('"')[0]
                    add = item.split('"AddressLine1":"')[1].split('"')[0] + ' ' + item.split('"AddressLine2":"')[1].split('"')[0] + ' ' + item.split('"AddressLine3":"')[1].split('"')[0]
                    add = add.strip()
                    typ = item.split('"AccountBrand":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    state = item.split('"StateProvince":"')[1].split('"')[0]
                    country = item.split('"Country":"')[1].split('"')[0]
                    phone = item.split('"Phone1":"')[1].split('"')[0]
                    zc = item.split('"PostalCode":"')[1].split('"')[0]
                    lat = item.split('"Latitude":"')[1].split('"')[0]
                    lng = item.split('"Longitude":"')[1].split('"')[0]
                    hours = ''
                    loc = 'https://www.internationaltrucks.com/dealer-locator?account=' + store
                    if '"AutoSalesHours":[{' in item:
                        days = item.split('"AutoSalesHours":[{')[1].split(']')[0].split('"StartDay":"')
                        for day in days:
                            if 'EndTime' in day:
                                hrs = day.split('"')[0] + ': ' + day.split('"StartTime":"')[1].split('"')[0].rsplit(':',1)[0] + '-' + day.split('"EndTime":"')[1].split('"')[0].rsplit(':',1)[0]
                                if hours == '':
                                    hours = hrs
                                else:
                                    if '0' in hrs:
                                        hours = hours + '; ' + hrs
                    else:
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    # print('Hawaii')
    locstr = 'Honolulu, HI'
    payload = {"searchType":"Location",
               "searchValue":locstr,
               "boxSearchCollection":[{"lat1":0,"long1":0,"lat2":0,"long2":0,
                                       "boxes":[]}],"filters":[],
               "hasSales":False,
               "hasService":False,
               "hasParts":False,
               "distance":1000000,
               "clientTime":"2020-07-01 10:30:37",
               "country":"USA",
               "brand":"INT",
               "sort":"nearToFar",
               "isDiamondEdge":False,
               "isLoves":False,
               "isSpeedCo":False}
    url = 'https://dealerlocator-api.internationaltrucks.com/api/v1/dealers/getdealers/'
    r = post(url, headers=headers, data=json.dumps(payload))
    website = 'internationaltrucks.com'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"FullAccountNumber":"' in line:
            items = line.split('{"FullAccountNumber":"')
            for item in items:
                if '"StateProvince":"' in item:
                    store = item.split('"')[0]
                    name = item.split('"AccountName":"')[1].split('"')[0]
                    add = item.split('"AddressLine1":"')[1].split('"')[0] + ' ' + item.split('"AddressLine2":"')[1].split('"')[0] + ' ' + item.split('"AddressLine3":"')[1].split('"')[0]
                    add = add.strip()
                    typ = item.split('"AccountBrand":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    state = item.split('"StateProvince":"')[1].split('"')[0]
                    country = item.split('"Country":"')[1].split('"')[0]
                    phone = item.split('"Phone1":"')[1].split('"')[0]
                    zc = item.split('"PostalCode":"')[1].split('"')[0]
                    lat = item.split('"Latitude":"')[1].split('"')[0]
                    lng = item.split('"Longitude":"')[1].split('"')[0]
                    hours = ''
                    loc = 'https://www.internationaltrucks.com/dealer-locator?account=' + store
                    if '"AutoSalesHours":[{' in item:
                        days = item.split('"AutoSalesHours":[{')[1].split(']')[0].split('"StartDay":"')
                        for day in days:
                            if 'EndTime' in day:
                                hrs = day.split('"')[0] + ': ' + day.split('"StartTime":"')[1].split('"')[0].rsplit(':',1)[0] + '-' + day.split('"EndTime":"')[1].split('"')[0].rsplit(':',1)[0]
                                if hours == '':
                                    hours = hrs
                                else:
                                    if '0' in hrs:
                                        hours = hours + '; ' + hrs
                    else:
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    for x in range(23, 50):
        for y in range(-63, -125, -1):
            # print(str(x) + ', ' + str(y))
            locstr = str(x) + ', ' + str(y)
            payload = {"searchType":"Location",
                       "searchValue":locstr,
                       "boxSearchCollection":[{"lat1":0,"long1":0,"lat2":0,"long2":0,
                                               "boxes":[]}],"filters":[],
                       "hasSales":False,
                       "hasService":False,
                       "hasParts":False,
                       "distance":1000000,
                       "clientTime":"2020-07-01 10:30:37",
                       "country":"USA",
                       "brand":"INT",
                       "sort":"nearToFar",
                       "isDiamondEdge":False,
                       "isLoves":False,
                       "isSpeedCo":False}
            url = 'https://dealerlocator-api.internationaltrucks.com/api/v1/dealers/getdealers/'
            r = post(url, headers=headers, data=json.dumps(payload))
            website = 'internationaltrucks.com'
            for line in r.iter_lines():
                line = str(line.decode('utf-8'))
                if '{"FullAccountNumber":"' in line:
                    items = line.split('{"FullAccountNumber":"')
                    for item in items:
                        if '"StateProvince":"' in item:
                            store = item.split('"')[0]
                            name = item.split('"AccountName":"')[1].split('"')[0]
                            add = item.split('"AddressLine1":"')[1].split('"')[0] + ' ' + item.split('"AddressLine2":"')[1].split('"')[0] + ' ' + item.split('"AddressLine3":"')[1].split('"')[0]
                            add = add.strip()
                            typ = item.split('"AccountBrand":"')[1].split('"')[0]
                            city = item.split('"City":"')[1].split('"')[0]
                            state = item.split('"StateProvince":"')[1].split('"')[0]
                            country = item.split('"Country":"')[1].split('"')[0]
                            phone = item.split('"Phone1":"')[1].split('"')[0]
                            zc = item.split('"PostalCode":"')[1].split('"')[0]
                            lat = item.split('"Latitude":"')[1].split('"')[0]
                            lng = item.split('"Longitude":"')[1].split('"')[0]
                            hours = ''
                            loc = 'https://www.internationaltrucks.com/dealer-locator?account=' + store
                            if '"AutoSalesHours":[{' in item:
                                days = item.split('"AutoSalesHours":[{')[1].split(']')[0].split('"StartDay":"')
                                for day in days:
                                    if 'EndTime' in day:
                                        hrs = day.split('"')[0] + ': ' + day.split('"StartTime":"')[1].split('"')[0].rsplit(':',1)[0] + '-' + day.split('"EndTime":"')[1].split('"')[0].rsplit(':',1)[0]
                                        if hours == '':
                                            hours = hrs
                                        else:
                                            if '0' in hrs:
                                                hours = hours + '; ' + hrs
                            else:
                                hours = '<MISSING>'
                            if phone == '':
                                phone = '<MISSING>'
                            if 'U' in country:
                                country = 'US'
                            else:
                                country = 'CA'
                            if store not in locs:
                                locs.append(store)
                                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

    for x in range(40, 70):
        for y in range(-52, -141, -1):
            # print(str(x) + ', ' + str(y))
            locstr = str(x) + ', ' + str(y)
            payload = {"searchType":"Location",
                       "searchValue":locstr,
                       "boxSearchCollection":[{"lat1":0,"long1":0,"lat2":0,"long2":0,
                                               "boxes":[]}],"filters":[],
                       "hasSales":False,
                       "hasService":False,
                       "hasParts":False,
                       "distance":1000000,
                       "clientTime":"2020-07-01 10:30:37",
                       "country":"Canada",
                       "brand":"INT",
                       "sort":"nearToFar",
                       "isDiamondEdge":False,
                       "isLoves":False,
                       "isSpeedCo":False}
            url = 'https://dealerlocator-api.internationaltrucks.com/api/v1/dealers/getdealers/'
            r = post(url, headers=headers, data=json.dumps(payload))
            website = 'internationaltrucks.com'
            for line in r.iter_lines():
                line = str(line.decode('utf-8'))
                if '{"FullAccountNumber":"' in line:
                    items = line.split('{"FullAccountNumber":"')
                    for item in items:
                        if '"StateProvince":"' in item:
                            store = item.split('"')[0]
                            name = item.split('"AccountName":"')[1].split('"')[0]
                            add = item.split('"AddressLine1":"')[1].split('"')[0] + ' ' + item.split('"AddressLine2":"')[1].split('"')[0] + ' ' + item.split('"AddressLine3":"')[1].split('"')[0]
                            add = add.strip()
                            typ = item.split('"AccountBrand":"')[1].split('"')[0]
                            city = item.split('"City":"')[1].split('"')[0]
                            state = item.split('"StateProvince":"')[1].split('"')[0]
                            country = item.split('"Country":"')[1].split('"')[0]
                            phone = item.split('"Phone1":"')[1].split('"')[0]
                            zc = item.split('"PostalCode":"')[1].split('"')[0]
                            lat = item.split('"Latitude":"')[1].split('"')[0]
                            lng = item.split('"Longitude":"')[1].split('"')[0]
                            hours = ''
                            loc = 'https://www.internationaltrucks.com/dealer-locator?account=' + store
                            if '"AutoSalesHours":[{' in item:
                                days = item.split('"AutoSalesHours":[{')[1].split(']')[0].split('"StartDay":"')
                                for day in days:
                                    if 'EndTime' in day:
                                        hrs = day.split('"')[0] + ': ' + day.split('"StartTime":"')[1].split('"')[0].rsplit(':',1)[0] + '-' + day.split('"EndTime":"')[1].split('"')[0].rsplit(':',1)[0]
                                        if hours == '':
                                            hours = hrs
                                        else:
                                            if '0' in hrs:
                                                hours = hours + '; ' + hrs
                            else:
                                hours = '<MISSING>'
                            if phone == '':
                                phone = '<MISSING>'
                            if 'U' in country:
                                country = 'US'
                            else:
                                country = 'CA'
                            if store not in locs:
                                locs.append(store)
                                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
