import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'authority': 'www.hilton.com',
           'origin': 'https://www.hilton.com'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    count = 0
    lids = []
    print('Pulling Locations...')
    payload = {"operationName":"hotelMapZones","variables":{"brandCode":"HW"},"query":"query hotelMapZones($brandCode: String) {\n  hotelMapZones(brandCode: $brandCode) {\n    id {\n      x\n      y\n      __typename\n    }\n    bounds {\n      southwest {\n        latitude\n        longitude\n        __typename\n      }\n      northeast {\n        latitude\n        longitude\n        __typename\n      }\n      __typename\n    }\n    countries {\n      countryCode\n      stateCodes\n      __typename\n    }\n    brandCodes\n    __typename\n  }\n}\n"}
    url = 'https://www.hilton.com/graphql/customer?appName=dx-shop-dream-ui&operationName=hotelMapZones'
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"id":{"x":' in line:
            items = line.split('{"id":{"x":')
            for item in items:
                if '"__typename":"HotelMapZoneId"' in item:
                    xc = item.split(',')[0]
                    yc = item.split('"y":')[1].split(',')[0]
                    lids.append(xc + '-' + yc)
    for lid in lids:
        xid = lid.split('-')[0]
        yid = lid.split('-')[1]
        url = 'https://www.hilton.com/graphql/customer?appName=dx-shop-dream-ui&operationName=hotelSummaryOptions&queryType=zone'
        payload = {"operationName":"hotelSummaryOptions","variables":{"brandCodes":["HW"],"currencyCode":"usd","language":"en","zone":{"x":xid,"y":yid}},"query":"query hotelSummaryOptions($brandCodes: [String!]!, $currencyCode: String!, $language: String!, $zone: HotelZoneInput) {\n  hotelSummaryOptions(brandCodes: $brandCodes, language: $language, input: {zone: $zone}) {\n    hotels {\n      _id: ctyhocn\n      amenityIds\n      brandCode\n      ctyhocn\n      currencyCode\n      distance\n      distanceFmt\n      homeUrl\n      homepageUrl\n      name\n      phoneNumber\n      address {\n        addressFmt\n        addressLine1\n        addressLine2\n        city\n        country\n        countryName\n        postalCode\n        state\n        stateName\n        __typename\n      }\n      coordinate {\n        latitude\n        longitude\n        __typename\n      }\n      thumbImage {\n        hiResSrc(height: 430, width: 612)\n        __typename\n      }\n      thumbnail: masterImage(variant: searchPropertyImageThumbnail) {\n        altText\n        variants {\n          size\n          url\n          __typename\n        }\n        __typename\n      }\n      leadRate {\n        lowest {\n          rateAmount(currencyCode: $currencyCode, decimal: 0, strategy: trunc)\n          rateAmountFmt(decimal: 0, strategy: trunc)\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
        r = session.post(url, headers=headers, data=json.dumps(payload))
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '{"_id":"' in line:
                items = line.split('{"_id":"')
                for item in items:
                    if '"amenityIds":' in item:
                        count = count + 1
                        store = item.split('"')[0]
                        website = 'homewoodsuites3.hilton.com'
                        typ = '<MISSING>'
                        hours = '<MISSING>'
                        loc = item.split(',"homeUrl":"')[1].split('"')[0]
                        name = item.split('"name":"')[1].split('"')[0]
                        try:
                            phone = item.split('"phoneNumber":"')[1].split('"')[0]
                        except:
                            phone = '<MISSING>'
                        add = item.split('"addressLine1":"')[1].split('"')[0]
                        try:
                            add = add + ' ' + item.split('"addressLine2":"')[1].split('"')[0]
                        except:
                            pass
                        city = item.split('"city":"')[1].split('"')[0]
                        country = item.split('"country":"')[1].split('"')[0]
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        state = item.split(',"state":"')[1].split('"')[0]
                        lat = item.split('"latitude":')[1].split(',')[0]
                        lng = item.split('"longitude":')[1].split(',')[0]
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        print(str(count) + ' Locations Found...')

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
