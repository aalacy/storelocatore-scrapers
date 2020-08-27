import csv
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
    url = 'https://cat-ms.esri.com/dls/cat/locations/en?f=json&forStorage=false&distanceUnit=mi&&searchType=location&maxResults=5000&searchDistance=5000&productDivId=1%2C6%2C3%2C5%2C4%2C8%2C7&serviceId=1%2C2&appId=n6HDEnXnYRTDAxFr&searchValue=-90%2C40'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '"dealerId":' in line:
            items = line.split('"dealerId":')
            for item in items:
                if '"territoryId":' in item:
                    store = item.split(',')[0]
                    website = 'cat.com'
                    hours = ''
                    name = item.split(',"dealerName":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    try:
                        country = item.split('"countryCode":"')[1].split('"')[0]
                    except:
                        country = ''
                    add = item.split('"siteAddress":"')[1].split('"')[0] + ' ' + item.split('"siteAddress1":"')[1].split('"')[0]
                    add = add.strip()
                    pnums = item.split('"phoneNumberTypeId":')
                    phone = '<MISSING>'
                    for pnum in pnums:
                        if '"phoneNumberType":"GENERAL INFO' in pnum:
                            phone = pnum.split('"phoneNumber":"')[1].split('"')[0]
                    city = item.split('"siteCity":"')[1].split('"')[0]
                    state = item.split('"siteState":"')[1].split('"')[0]
                    zc = item.split(',"sitePostal":"')[1].split('"')[0]
                    typ = ''
                    snums = item.split('{"serviceId":')
                    donetyps = []
                    for snum in snums:
                        if '"serviceDesc":"' in snum:
                            styp = snum.split('"serviceDesc":"')[1].split('"')[0]
                            if typ == '':
                                typ = styp
                            else:
                                if styp not in donetyps:
                                    donetyps.append(styp)
                                    typ = typ + ', ' + styp
                    try:
                        if '"storeHoursMon":""' in item:
                            hours = 'Mon: Closed'
                        else:
                            hours = 'Mon: ' + item.split('"storeHoursMon":"')[1].split('"')[0]
                        if '"storeHoursTue":""' in item:
                            hours = hours + '; Tue: Closed'
                        else:
                            hours = hours + '; Tue: ' + item.split('"storeHoursTue":"')[1].split('"')[0]
                        if '"storeHoursWed":""' in item:
                            hours = hours + '; Wed: Closed'
                        else:
                            hours = hours + '; Wed: ' + item.split('"storeHoursTue":"')[1].split('"')[0]
                        if '"storeHoursThu":""' in item:
                            hours = hours + '; Thu: Closed'
                        else:
                            hours = hours + '; Thu: ' + item.split('"storeHoursTue":"')[1].split('"')[0]
                        if '"storeHoursFri":""' in item:
                            hours = hours + '; Fri: Closed'
                        else:
                            hours = hours + '; Fri: ' + item.split('"storeHoursTue":"')[1].split('"')[0]
                        if '"storeHoursSat":""' in item:
                            hours = hours + '; Sat: Closed'
                        else:
                            hours = hours + '; Sat: ' + item.split('"storeHoursTue":"')[1].split('"')[0]
                        if '"storeHoursSun":""' in item:
                            hours = hours + '; Sun: Closed'
                        else:
                            hours = hours + '; Sun: ' + item.split('"storeHoursTue":"')[1].split('"')[0]
                    except:
                        hours = '<MISSING>'
                    if country == 'CA' or country == 'US':
                        if 'Sales"},' in item:
                            loc = '<MISSING>'
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
