import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'x-requested-with': 'XMLHttpRequest',
           'accept': 'application/json, text/javascript, */*; q=0.01'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://hosted.where2getit.com/marazziusa/rest/locatorsearch?like=0.5591100517070091&lang=en_US'
    payload = {"request":{"appkey":"D07A672A-3D5E-11EA-9DD6-ABD5D0784D66",
                          "formdata":{"dynamicSearch":"true","geoip":"false",
                                      "dataview":"store_default","limit":1000,
                                      "order":"PREMIERSTATEMENTSDEALER asc, SHOWROOM asc, LOCATION_RATING::numeric desc nulls last, _distance",
                                      "geolocs":{"geoloc":[{"addressline":"55441","country":"","latitude":"","longitude":""}]},"searchradius":"5000",
                                      "stateonly":"1","where":{"clientkey":{"distinctfrom":"12345"},
                                                               "badge":{"distinctfrom":"Not On Locator"},
                                                               "marazzi":{"eq":"1"},"or":{"showroom":{"eq":"1"},
                                                                                          "premierstatementsdealer":{"eq":""},
                                                                                          "authorizeddealer":{"eq":"1"},
                                                                                          "daltileservicecenter":{"eq":"1"},
                                                                                          "distributor":{"eq":"1"},
                                                                                          "tile_mosaics":{"eq":""},
                                                                                          "stone_slab_countertops":{"eq":""}}},
                                      "true":"1","false":"0"}}}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for line in r.iter_lines():
        if '"six_packcontent2":' in line:
            items = line.split('"six_packcontent2":')
            for item in items:
                if '{ "response":' not in item:
                    lat = item.split('"latitude":"')[1].split('"')[0]
                    lng = item.split('"longitude":"')[1].split('"')[0]
                    zc = item.split(',"postalcode":"')[1].split('"')[0]
                    website = 'marazziusa.com'
                    country = 'US'
                    name = item.split('"name":"')[1].split('"')[0]
                    try:
                        typ = item.split('"storetype":"')[1].split('"')[0]
                    except:
                        typ = '<MISSING>'
                    loc = '<MISSING>'
                    state = item.split('"state":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    add = item.split('"address1":"')[1].split('"')[0]
                    try:
                        phone = item.split('"phone":"')[1].split('"')[0]
                    except:
                        phone = '<MISSING>'
                    hours = '<MISSING>'
                    store = item.split('"clientkey":"')[1].split('"')[0]
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

        payload = {"request":{"appkey":"D07A672A-3D5E-11EA-9DD6-ABD5D0784D66",
                          "formdata":{"dynamicSearch":"true","geoip":"false",
                                      "dataview":"store_default","limit":1000,
                                      "order":"PREMIERSTATEMENTSDEALER asc, SHOWROOM asc, LOCATION_RATING::numeric desc nulls last, _distance",
                                      "geolocs":{"geoloc":[{"addressline":"85001","country":"","latitude":"","longitude":""}]},"searchradius":"5000",
                                      "stateonly":"1","where":{"clientkey":{"distinctfrom":"12345"},
                                                               "badge":{"distinctfrom":"Not On Locator"},
                                                               "marazzi":{"eq":"1"},"or":{"showroom":{"eq":"1"},
                                                                                          "premierstatementsdealer":{"eq":""},
                                                                                          "authorizeddealer":{"eq":"1"},
                                                                                          "daltileservicecenter":{"eq":"1"},
                                                                                          "distributor":{"eq":"1"},
                                                                                          "tile_mosaics":{"eq":""},
                                                                                          "stone_slab_countertops":{"eq":""}}},
                                      "true":"1","false":"0"}}}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for line in r.iter_lines():
        if '"six_packcontent2":' in line:
            items = line.split('"six_packcontent2":')
            for item in items:
                if '{ "response":' not in item:
                    lat = item.split('"latitude":"')[1].split('"')[0]
                    lng = item.split('"longitude":"')[1].split('"')[0]
                    zc = item.split(',"postalcode":"')[1].split('"')[0]
                    website = 'marazziusa.com'
                    country = 'US'
                    name = item.split('"name":"')[1].split('"')[0]
                    try:
                        typ = item.split('"storetype":"')[1].split('"')[0]
                    except:
                        typ = '<MISSING>'
                    loc = '<MISSING>'
                    state = item.split('"state":"')[1].split('"')[0]
                    try:
                        city = item.split('"city":"')[1].split('"')[0]
                    except:
                        city = '<MISSING>'
                    add = item.split('"address1":"')[1].split('"')[0]
                    try:
                        phone = item.split('"phone":"')[1].split('"')[0]
                    except:
                        phone = '<MISSING>'
                    hours = '<MISSING>'
                    store = item.split('"clientkey":"')[1].split('"')[0]
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

        payload = {"request":{"appkey":"D07A672A-3D5E-11EA-9DD6-ABD5D0784D66",
                          "formdata":{"dynamicSearch":"true","geoip":"false",
                                      "dataview":"store_default","limit":1000,
                                      "order":"PREMIERSTATEMENTSDEALER asc, SHOWROOM asc, LOCATION_RATING::numeric desc nulls last, _distance",
                                      "geolocs":{"geoloc":[{"addressline":"77001","country":"","latitude":"","longitude":""}]},"searchradius":"5000",
                                      "stateonly":"1","where":{"clientkey":{"distinctfrom":"12345"},
                                                               "badge":{"distinctfrom":"Not On Locator"},
                                                               "marazzi":{"eq":"1"},"or":{"showroom":{"eq":"1"},
                                                                                          "premierstatementsdealer":{"eq":""},
                                                                                          "authorizeddealer":{"eq":"1"},
                                                                                          "daltileservicecenter":{"eq":"1"},
                                                                                          "distributor":{"eq":"1"},
                                                                                          "tile_mosaics":{"eq":""},
                                                                                          "stone_slab_countertops":{"eq":""}}},
                                      "true":"1","false":"0"}}}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for line in r.iter_lines():
        if '"six_packcontent2":' in line:
            items = line.split('"six_packcontent2":')
            for item in items:
                if '{ "response":' not in item:
                    lat = item.split('"latitude":"')[1].split('"')[0]
                    lng = item.split('"longitude":"')[1].split('"')[0]
                    zc = item.split(',"postalcode":"')[1].split('"')[0]
                    website = 'marazziusa.com'
                    country = 'US'
                    name = item.split('"name":"')[1].split('"')[0]
                    try:
                        typ = item.split('"storetype":"')[1].split('"')[0]
                    except:
                        typ = '<MISSING>'
                    loc = '<MISSING>'
                    state = item.split('"state":"')[1].split('"')[0]
                    try:
                        city = item.split('"city":"')[1].split('"')[0]
                    except:
                        city = '<MISSING>'
                    add = item.split('"address1":"')[1].split('"')[0]
                    try:
                        phone = item.split('"phone":"')[1].split('"')[0]
                    except:
                        phone = '<MISSING>'
                    hours = '<MISSING>'
                    store = item.split('"clientkey":"')[1].split('"')[0]
                    if store not in locs:
                        locs.append(store)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
