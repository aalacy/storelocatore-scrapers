import csv
import urllib2
import requests
import time

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    urls = ['https://stores.advanceautoparts.com/']
    states = []
    cities = []
    locs = []
    allstores = []
    website = 'advanceautoparts.com'
    typ = '<MISSING>'
    country = '<MISSING>'
    canada = ['PE','NB','MB','BC','ON','QC','AB','NS','NL']
    for url in urls:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<a class="c-directory-list-content-item-link" href="' in line:
                items = line.split('<a class="c-directory-list-content-item-link" href="')
                for item in items:
                    if '<span class="c-directory-list-content-item-count">(' in item:
                        count = item.split('<span class="c-directory-list-content-item-count">(')[1].split(')')[0]
                        if count != '1':
                            states.append('https://stores.advanceautoparts.com/' + item.split('"')[0].replace('..',''))
                        else:
                            locs.append('https://stores.advanceautoparts.com/' + item.split('"')[0].replace('..',''))
    for state in states:
        print('Pulling State %s...' % state)
        r = session.get(state, headers=headers)
        for line in r.iter_lines():
            if 'a class="c-directory-list-content-item-link" href="' in line:
                items = line.split('<a class="c-directory-list-content-item-link" href="')
                for item in items:
                    if '<span class="c-directory-list-content-item-count">(' in item:
                        count = item.split('<span class="c-directory-list-content-item-count">(')[1].split(')')[0]
                        if count != '1':
                            cities.append('https://stores.advanceautoparts.com/' + item.split('"')[0].replace('..',''))
                        else:
                            locs.append('https://stores.advanceautoparts.com/' + item.split('"')[0].replace('..',''))
                                
    for city in cities:
        CFound = True
        while CFound:
            try:
                CFound = False
                print('Pulling City %s...' % city)
                coords = []
                stores = []
                typ = 'Advance Auto Parts'
                name = ''
                r = session.get(city, headers=headers, timeout=5)
                for line in r.iter_lines():
                    if '<div class="LocationName-geo">' in line:
                        name = name + ' ' + line.split('<div class="LocationName-geo">')[1].split('<')[0].strip()
                        add = line.split('class="c-address-street-1"')[1].split('>')[1].split('<')[0]
                        city = line.split('<span class="c-address-city"')[1].split('>')[1].split('<')[0]
                        try:
                            state = line.split('class="c-address-state"')[1].split('>')[1].split('<')[0]
                        except:
                            state = ''
                        if state in canada:
                            country = 'CA'
                        else:
                            country = 'US'
                        zc = line.split('"c-address-postal-code" >')[1].split('<')[0]
                        try:
                            phone = line.split('c-phone-main-number-link"')[1].split('>')[1].split('<')[0]
                        except:
                            phone = '<MISSING>'
                        try:
                            hours = 'Mon: ' + line.split('"day":"MONDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"MONDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = 'Mon: Closed'
                        try:
                            hours = hours + '; Tue: ' + line.split('"day":"TUESDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"TUESDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Tue: Closed'
                        try:
                            hours = hours + '; Wed: ' + line.split('"day":"WEDNESDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"WEDNESDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Wed: Closed'
                        try:
                            hours = hours + '; Thu: ' + line.split('"day":"THURSDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"THURSDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Thu: Closed'
                        try:
                            hours = hours + '; Fri: ' + line.split('"day":"FRIDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"FRIDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Fri: Closed'
                        try:
                            hours = hours + '; Sat: ' + line.split('"day":"SATURDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"SATURDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Sat: Closed'
                        try:
                            hours = hours + '; Sun: ' + line.split('"day":"SUNDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"SUNDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Sun: Closed'
                        stores.append(name.replace('|','-') + '|' + add.replace('|','-') + '|' + city.replace('|','-') + '|' + state.replace('|','-') + '|' + zc.replace('|','-') + '|' + country.replace('|','-') + '|' + phone.replace('|','-') + '|' + hours.replace('|','-'))
                        try:
                            name = line.split('<span class="LocationName"><span class="LocationName-brand">')[1].split('</span></span>')[0].replace('<span>','').replace('  ',' ').strip()
                        except:
                            pass
                    if '<span class="LocationName"><span class="LocationName-brand">' in line:
                        name = line.split('<span class="LocationName"><span class="LocationName-brand">')[1].split('</span></span>')[0].replace('<span>','').replace('  ',' ').strip()
                    if ',"id":' in line:
                        items = line.split(',"id":')
                        for item in items:
                            if '"longitude":' in item:
                                latlng = item.split(',')[0] + '|' + item.split('"latitude":')[1].split(',')[0] + '|' + item.split('"longitude":')[1].split(',')[0]
                                coords.append(latlng)
                for x in range(0, len(stores)):
                    name = stores[x].split('|')[0]
                    add = stores[x].split('|')[1]
                    city = stores[x].split('|')[2]
                    state = stores[x].split('|')[3]
                    zc = stores[x].split('|')[4]
                    country = stores[x].split('|')[5]
                    phone = stores[x].split('|')[6]
                    hours = stores[x].split('|')[7]
                    store = coords[x].split('|')[0]
                    lat = coords[x].split('|')[1]
                    lng = coords[x].split('|')[2]
                    if store not in allstores:
                        allstores.append(store)
                        if state == '':
                            state = 'PR'
                        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                CFound = True
    for loc in locs:
        LFound = True
        while LFound:
            try:
                LFound = False
                print('Pulling Location %s...' % loc)
                typ = 'Advance Auto Parts'
                r = session.get(loc, headers=headers, timeout=5)
                name = ''
                add = ''
                city = ''
                state = ''
                zc = ''
                lat = ''
                lng = ''
                hours = ''
                country = ''
                phone = ''
                store = ''
                LocFound = False
                for line in r.iter_lines():
                    if '"store_id":"' in line:
                        store = line.split('"store_id":"')[1].split('"')[0]
                    if '<div class="LocationName-geo">' in line and LocFound is False:
                        LocFound = True
                        name = line.split('<div class="LocationName-geo">')[1].split('<')[0]
                        add = line.split('class="c-address-street-1"')[1].split('>')[1].split('<')[0]
                        if '<span class="c-address-street-2"' in line:
                            add = add + ' ' + line.split('<span class="c-address-street-2"')[1].split('>')[1].split('<')[0]
                        city = line.split('<span class="c-address-city"')[1].split('>')[1].split('<')[0]
                        try:
                            state = line.split('class="c-address-state"')[1].split('>')[1].split('<')[0]
                        except:
                            state = '<MISSING>'
                        if state in canada:
                            country = 'CA'
                        else:
                            country = 'US'
                        zc = line.split('"c-address-postal-code"')[1].split('>')[1].split('<')[0]
                        try:
                            phone = line.split('c-phone-main-number-link"')[1].split('>')[1].split('<')[0]
                        except:
                            phone = '<MISSING>'
                        try:
                            hours = 'Mon: ' + line.split('"day":"MONDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"MONDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = 'Mon: Closed'
                        try:
                            hours = hours + '; Tue: ' + line.split('"day":"TUESDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"TUESDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Tue: Closed'
                        try:
                            hours = hours + '; Wed: ' + line.split('"day":"WEDNESDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"WEDNESDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Wed: Closed'
                        try:
                            hours = hours + '; Thu: ' + line.split('"day":"THURSDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"THURSDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Thu: Closed'
                        try:
                            hours = hours + '; Fri: ' + line.split('"day":"FRIDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"FRIDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Fri: Closed'
                        try:
                            hours = hours + '; Sat: ' + line.split('"day":"SATURDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"SATURDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Sat: Closed'
                        try:
                            hours = hours + '; Sun: ' + line.split('"day":"SUNDAY","')[1].split('"start":')[1].split('}')[0] + '-' + line.split('"day":"SUNDAY","')[1].split('"end":')[1].split(',')[0]
                        except:
                            hours = hours + '; Sun: Closed'
                        stores.append(name.replace('|','-') + '|' + add.replace('|','-') + '|' + city.replace('|','-') + '|' + state.replace('|','-') + '|' + zc.replace('|','-') + '|' + country.replace('|','-') + '|' + phone.replace('|','-') + '|' + hours.replace('|','-'))
                    if '<meta itemprop="latitude" content="' in line:
                        lat = line.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                        lng = line.split('<meta itemprop="longitude" content="')[1].split('"')[0]
                if store not in allstores:
                    allstores.append(store)
                    if state == '':
                        state = 'PR'
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                LFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
