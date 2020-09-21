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
    allstores = []
    urls = ['https://cat-ms.esri.com/dls/cat/locations/en?f=json&forStorage=false&distanceUnit=mi&&searchType=location&maxResults=5000&searchDistance=5000&productDivId=1%2C6%2C3%2C5%2C4%2C8%2C7%2C2&serviceId=1%2C2%2C3%2C4%2C8%2C9%2C10%2C5%2C6%2C7%2C12&appId=n6HDEnXnYRTDAxFr&searchValue=-115.8431267%2C35.2270869','https://cat-ms.esri.com/dls/cat/locations/en?f=json&forStorage=false&distanceUnit=mi&&searchType=location&maxResults=5000&searchDistance=5000&productDivId=1%2C6%2C3%2C5%2C4%2C8%2C7&serviceId=1%2C2&appId=n6HDEnXnYRTDAxFr&searchValue=-90%2C40','https://cat-ms.esri.com/dls/cat/locations/en?f=json&forStorage=false&distanceUnit=mi&&searchType=location&maxResults=5000&searchDistance=5000&productDivId=1%2C6%2C3%2C5%2C4%2C8%2C7%2C2&serviceId=1%2C2%2C3%2C4%2C8%2C9%2C10%2C5%2C6%2C7%2C12&appId=n6HDEnXnYRTDAxFr&searchValue=-80.8431267%2C35.2270869']
    for url in urls:
        print(url)
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '"dealerId":' in line:
                items = line.split('"dealerId":')
                for item in items:
                    if '"territoryId":' in item:
                        store = item.split('"dealerLocationId":')[1].split(',')[0]
                        website = 'cat.com'
                        hours = ''
                        name = item.split(',"dealerName":"')[1].split('"')[0].encode("ascii", errors="ignore").decode()
                        lat = item.split('"latitude":')[1].split(',')[0]
                        lng = item.split('"longitude":')[1].split(',')[0]
                        try:
                            country = item.split('"countryCode":"')[1].split('"')[0]
                        except:
                            country = ''
                        add = item.split('"siteAddress":"')[1].split('"')[0] + ' ' + item.split('"siteAddress1":"')[1].split('"')[0]
                        add = add.strip().encode("ascii", errors="ignore").decode()
                        pnums = item.split('"phoneNumberTypeId":')
                        phone = '<MISSING>'
                        for pnum in pnums:
                            if '"phoneNumberType":"GENERAL INFO' in pnum:
                                phone = pnum.split('"phoneNumber":"')[1].split('"')[0].encode("ascii", errors="ignore").decode()
                        city = item.split('"siteCity":"')[1].split('"')[0].encode("ascii", errors="ignore").decode()
                        state = item.split('"siteState":"')[1].split('"')[0]
                        zc = item.split(',"sitePostal":"')[1].split('"')[0]
                        typ = ''
                        snums = item.split('{"serviceId":')
                        donetyps = []
                        for snum in snums:
                            if '"serviceDesc":"' in snum:
                                styp = snum.split('"serviceDesc":"')[1].split('"')[0].encode("ascii", errors="ignore").decode()
                                if typ == '':
                                    typ = styp
                                else:
                                    if styp not in donetyps:
                                        donetyps.append(styp)
                                        typ = typ + ', ' + styp
                        try:
                            if '"storeHoursMon":""' in item:
                                hours = hours + '; Mon: Closed'
                            else:
                                opn = item.split('"storeHoursMon":"')[1].split(' ')[0]
                                close = item.split('"storeHoursMon":"')[1].split(' - ')[1].split('"')[0]
                                opn = opn[:2] + ':' + opn[-2:]
                                close = close[:2] + ':' + close[-2:]
                                hours = hours + '; Mon: ' + opn + '-' + close
                            if '"storeHoursTue":""' in item:
                                hours = hours + '; Tue: Closed'
                            else:
                                opn = item.split('"storeHoursTue":"')[1].split(' ')[0]
                                close = item.split('"storeHoursTue":"')[1].split(' - ')[1].split('"')[0]
                                opn = opn[:2] + ':' + opn[-2:]
                                close = close[:2] + ':' + close[-2:]
                                hours = hours + '; Tue: ' + opn + '-' + close
                            if '"storeHoursWed":""' in item:
                                hours = hours + '; Wed: Closed'
                            else:
                                opn = item.split('"storeHoursWed":"')[1].split(' ')[0]
                                close = item.split('"storeHoursWed":"')[1].split(' - ')[1].split('"')[0]
                                opn = opn[:2] + ':' + opn[-2:]
                                close = close[:2] + ':' + close[-2:]
                                hours = hours + '; Wed: ' + opn + '-' + close
                            if '"storeHoursThu:""' in item:
                                hours = hours + '; Thu: Closed'
                            else:
                                opn = item.split('"storeHoursThu":"')[1].split(' ')[0]
                                close = item.split('"storeHoursThu":"')[1].split(' - ')[1].split('"')[0]
                                opn = opn[:2] + ':' + opn[-2:]
                                close = close[:2] + ':' + close[-2:]
                                hours = hours + '; Thu: ' + opn + '-' + close
                            if '"storeHoursFri":""' in item:
                                hours = hours + '; Fri: Closed'
                            else:
                                opn = item.split('"storeHoursFri":"')[1].split(' ')[0]
                                close = item.split('"storeHoursFri":"')[1].split(' - ')[1].split('"')[0]
                                opn = opn[:2] + ':' + opn[-2:]
                                close = close[:2] + ':' + close[-2:]
                                hours = hours + '; Fri: ' + opn + '-' + close
                            if '"storeHoursSat":""' in item:
                                hours = hours + '; Sat: Closed'
                            else:
                                opn = item.split('"storeHoursSat":"')[1].split(' ')[0]
                                close = item.split('"storeHoursSat":"')[1].split(' - ')[1].split('"')[0]
                                opn = opn[:2] + ':' + opn[-2:]
                                close = close[:2] + ':' + close[-2:]
                                hours = hours + '; Sat: ' + opn + '-' + close
                            if '"storeHoursSun":""' in item:
                                hours = hours + '; Sun: Closed'
                            else:
                                opn = item.split('"storeHoursSun":"')[1].split(' ')[0]
                                close = item.split('"storeHoursSun":"')[1].split(' - ')[1].split('"')[0]
                                opn = opn[:2] + ':' + opn[-2:]
                                close = close[:2] + ':' + close[-2:]
                                hours = hours + '; Sun: ' + opn + '-' + close
                        except:
                            hours = '<MISSING>'
                        if country == 'CA' or country == 'US':
                            if 'Sales"},' in item:
                                loc = '<MISSING>'
                                if state == '':
                                    state = '<MISSING>'
                                if store not in allstores:
                                    allstores.append(store)
                                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    for x in range(20, 70, 5):
        for y in range(-60, -160, -5):
            print(str(x) + ',' + str(y))
            url = 'https://cat-ms.esri.com/dls/cat/locations/en?f=json&forStorage=false&distanceUnit=mi&&searchType=location&maxResults=1000&searchDistance=1000&productDivId=1%2C6%2C3%2C5%2C4%2C8%2C7%2C2&serviceId=1%2C2%2C3%2C4%2C8%2C9%2C10%2C5%2C6%2C7%2C12&appId=n6HDEnXnYRTDAxFr&searchValue=' + str(y) + '%2C' + str(x)
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                line = str(line.decode('utf-8'))
                if '"dealerId":' in line:
                    items = line.split('"dealerId":')
                    for item in items:
                        if '"territoryId":' in item:
                            store = item.split('"dealerLocationId":')[1].split(',')[0]
                            website = 'cat.com'
                            hours = ''
                            name = item.split(',"dealerName":"')[1].split('"')[0].encode("ascii", errors="ignore").decode()
                            lat = item.split('"latitude":')[1].split(',')[0]
                            lng = item.split('"longitude":')[1].split(',')[0]
                            try:
                                country = item.split('"countryCode":"')[1].split('"')[0]
                            except:
                                country = ''
                            add = item.split('"siteAddress":"')[1].split('"')[0] + ' ' + item.split('"siteAddress1":"')[1].split('"')[0]
                            add = add.strip().encode("ascii", errors="ignore").decode()
                            pnums = item.split('"phoneNumberTypeId":')
                            phone = '<MISSING>'
                            for pnum in pnums:
                                if '"phoneNumberType":"GENERAL INFO' in pnum:
                                    phone = pnum.split('"phoneNumber":"')[1].split('"')[0].encode("ascii", errors="ignore").decode()
                            city = item.split('"siteCity":"')[1].split('"')[0].encode("ascii", errors="ignore").decode()
                            state = item.split('"siteState":"')[1].split('"')[0]
                            zc = item.split(',"sitePostal":"')[1].split('"')[0]
                            typ = ''
                            snums = item.split('{"serviceId":')
                            donetyps = []
                            for snum in snums:
                                if '"serviceDesc":"' in snum:
                                    styp = snum.split('"serviceDesc":"')[1].split('"')[0].encode("ascii", errors="ignore").decode()
                                    if typ == '':
                                        typ = styp
                                    else:
                                        if styp not in donetyps:
                                            donetyps.append(styp)
                                            typ = typ + ', ' + styp
                            try:
                                if '"storeHoursMon":""' in item:
                                    hours = hours + '; Mon: Closed'
                                else:
                                    opn = item.split('"storeHoursMon":"')[1].split(' ')[0]
                                    close = item.split('"storeHoursMon":"')[1].split(' - ')[1].split('"')[0]
                                    opn = opn[:2] + ':' + opn[-2:]
                                    close = close[:2] + ':' + close[-2:]
                                    hours = hours + '; Mon: ' + opn + '-' + close
                                if '"storeHoursTue":""' in item:
                                    hours = hours + '; Tue: Closed'
                                else:
                                    opn = item.split('"storeHoursTue":"')[1].split(' ')[0]
                                    close = item.split('"storeHoursTue":"')[1].split(' - ')[1].split('"')[0]
                                    opn = opn[:2] + ':' + opn[-2:]
                                    close = close[:2] + ':' + close[-2:]
                                    hours = hours + '; Tue: ' + opn + '-' + close
                                if '"storeHoursWed":""' in item:
                                    hours = hours + '; Wed: Closed'
                                else:
                                    opn = item.split('"storeHoursWed":"')[1].split(' ')[0]
                                    close = item.split('"storeHoursWed":"')[1].split(' - ')[1].split('"')[0]
                                    opn = opn[:2] + ':' + opn[-2:]
                                    close = close[:2] + ':' + close[-2:]
                                    hours = hours + '; Wed: ' + opn + '-' + close
                                if '"storeHoursThu:""' in item:
                                    hours = hours + '; Thu: Closed'
                                else:
                                    opn = item.split('"storeHoursThu":"')[1].split(' ')[0]
                                    close = item.split('"storeHoursThu":"')[1].split(' - ')[1].split('"')[0]
                                    opn = opn[:2] + ':' + opn[-2:]
                                    close = close[:2] + ':' + close[-2:]
                                    hours = hours + '; Thu: ' + opn + '-' + close
                                if '"storeHoursFri":""' in item:
                                    hours = hours + '; Fri: Closed'
                                else:
                                    opn = item.split('"storeHoursFri":"')[1].split(' ')[0]
                                    close = item.split('"storeHoursFri":"')[1].split(' - ')[1].split('"')[0]
                                    opn = opn[:2] + ':' + opn[-2:]
                                    close = close[:2] + ':' + close[-2:]
                                    hours = hours + '; Fri: ' + opn + '-' + close
                                if '"storeHoursSat":""' in item:
                                    hours = hours + '; Sat: Closed'
                                else:
                                    opn = item.split('"storeHoursSat":"')[1].split(' ')[0]
                                    close = item.split('"storeHoursSat":"')[1].split(' - ')[1].split('"')[0]
                                    opn = opn[:2] + ':' + opn[-2:]
                                    close = close[:2] + ':' + close[-2:]
                                    hours = hours + '; Sat: ' + opn + '-' + close
                                if '"storeHoursSun":""' in item:
                                    hours = hours + '; Sun: Closed'
                                else:
                                    opn = item.split('"storeHoursSun":"')[1].split(' ')[0]
                                    close = item.split('"storeHoursSun":"')[1].split(' - ')[1].split('"')[0]
                                    opn = opn[:2] + ':' + opn[-2:]
                                    close = close[:2] + ':' + close[-2:]
                                    hours = hours + '; Sun: ' + opn + '-' + close
                            except:
                                hours = '<MISSING>'
                            if country == 'CA' or country == 'US':
                                if 'Sales"},' in item:
                                    loc = '<MISSING>'
                                    if state == '':
                                        state = '<MISSING>'
                                    if store not in allstores:
                                        allstores.append(store)
                                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
