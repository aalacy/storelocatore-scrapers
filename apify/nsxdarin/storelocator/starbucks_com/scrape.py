import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
import datetime
from sgzip import sgzip

weekday = datetime.datetime.today().weekday()

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'accept': 'application/json',
           'x-requested-with': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    allcoords = []
    coords = []
    for coord in sgzip.coords_for_radius(50):
        x = coord[0]
        y = coord[1]
        latround = round(float(x), 2)
        lnground = round(float(y), 2)
        #print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        url = 'https://www.starbucks.com/bff/locations?lat=' + str(x) + '&lng=' + str(y)
        r = session.get(url, headers=headers)
        array = json.loads(r.content)
        num = len(array['stores'])
        for item in array['stores']:
            website = 'starbucks.com'
            store = item['storeNumber']
            name = item['name']
            phone = item['phoneNumber']
            lat = item['coordinates']['latitude']
            lng = item['coordinates']['longitude']
            add = item['address']['streetAddressLine1']
            try:
                add = add + ' ' + item['address']['streetAddressLine2']
            except:
                pass
            try:
                add = add + ' ' + item['address']['streetAddressLine3']
            except:
                pass
            add = add.strip()
            city = item['address']['city']
            state = item['address']['countrySubdivisionCode']
            country = item['address']['countryCode']
            zc = item['address']['postalCode']
            typ = item['brandName']
            hours = ''
            weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
            today = weekdays[weekday]
            tom = weekdays[(weekday + 1) % 7]
            try:
                hours = item['schedule'][0]['dayName'] + ': ' + item['schedule'][0]['hours']
                hours = hours + '; ' + item['schedule'][1]['dayName'] + ': ' + item['schedule'][1]['hours']
                hours = hours + '; ' + item['schedule'][2]['dayName'] + ': ' + item['schedule'][2]['hours']
                hours = hours + '; ' + item['schedule'][3]['dayName'] + ': ' + item['schedule'][3]['hours']
                hours = hours + '; ' + item['schedule'][4]['dayName'] + ': ' + item['schedule'][4]['hours']
                hours = hours + '; ' + item['schedule'][5]['dayName'] + ': ' + item['schedule'][5]['hours']
                hours = hours + '; ' + item['schedule'][6]['dayName'] + ': ' + item['schedule'][6]['hours']
                hours = hours.replace('Today',today).replace('Tomorrow',tom)
            except:
                pass
            if country == 'PR':
                country = 'US'
            if country == 'US':
                if store not in ids:
                    ids.append(store)
                    if phone is None or phone == '':
                        phone = '<MISSING>'
                    if hours is None or hours == '':
                        hours = '<MISSING>'
                    if zc is None or zc == '':
                        zc = '<MISSING>'
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                else:
                    num = num - 1
        if num >= 1:
            newcoord = str(latround + 0.05) + ',' + str(lnground)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround + 0.05) + ',' + str(lnground + 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround + 0.05) + ',' + str(lnground - 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround) + ',' + str(lnground - 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround) + ',' + str(lnground + 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround - 0.05) + ',' + str(lnground)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround - 0.05) + ',' + str(lnground + 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround - 0.05) + ',' + str(lnground - 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
    while len(coords) > 0:
        PageFound = True
        #print('%s Remaining...' % str(len(coords)))
        x = coords[0].split(',')[0]
        y = coords[0].split(',')[1]
        coords.pop(0)
        latround = round(float(x), 2)
        lnground = round(float(y), 2)
        while PageFound:
            try:
                PageFound = False
                #print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
                url = 'https://www.starbucks.com/bff/locations?lat=' + str(x) + '&lng=' + str(y)
                r = session.get(url, headers=headers, timeout=5)
                array = json.loads(r.content)
                num = len(array['stores'])
                for item in array['stores']:
                    website = 'starbucks.com'
                    store = item['storeNumber']
                    name = item['name']
                    phone = item['phoneNumber']
                    lat = item['coordinates']['latitude']
                    lng = item['coordinates']['longitude']
                    add = item['address']['streetAddressLine1']
                    try:
                        add = add + ' ' + item['address']['streetAddressLine2']
                    except:
                        pass
                    try:
                        add = add + ' ' + item['address']['streetAddressLine3']
                    except:
                        pass
                    add = add.strip()
                    city = item['address']['city']
                    state = item['address']['countrySubdivisionCode']
                    country = item['address']['countryCode']
                    zc = item['address']['postalCode']
                    typ = item['brandName']
                    hours = ''
                    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                    today = weekdays[weekday]
                    tom = weekdays[(weekday + 1) % 7]
                    try:
                        hours = item['schedule'][0]['dayName'] + ': ' + item['schedule'][0]['hours']
                        hours = hours + '; ' + item['schedule'][1]['dayName'] + ': ' + item['schedule'][1]['hours']
                        hours = hours + '; ' + item['schedule'][2]['dayName'] + ': ' + item['schedule'][2]['hours']
                        hours = hours + '; ' + item['schedule'][3]['dayName'] + ': ' + item['schedule'][3]['hours']
                        hours = hours + '; ' + item['schedule'][4]['dayName'] + ': ' + item['schedule'][4]['hours']
                        hours = hours + '; ' + item['schedule'][5]['dayName'] + ': ' + item['schedule'][5]['hours']
                        hours = hours + '; ' + item['schedule'][6]['dayName'] + ': ' + item['schedule'][6]['hours']
                        hours = hours.replace('Today',today).replace('Tomorrow',tom)
                    except:
                        pass
                    if country == 'PR':
                        country = 'US'
                    if country == 'US':
                        if store not in ids:
                            ids.append(store)
                            if phone is None or phone == '':
                                phone = '<MISSING>'
                            if hours is None or hours == '':
                                hours = '<MISSING>'
                            if zc is None or zc == '':
                                zc = '<MISSING>'
                            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                        else:
                            num = num - 1
                if num >= 1:
                    newcoord = str(latround + 0.03) + ',' + str(lnground)
                    if newcoord not in allcoords:
                        coords.append(newcoord)
                        allcoords.append(newcoord)
                    newcoord = str(latround + 0.03) + ',' + str(lnground + 0.03)
                    if newcoord not in allcoords:
                        coords.append(newcoord)
                        allcoords.append(newcoord)
                    newcoord = str(latround + 0.03) + ',' + str(lnground - 0.03)
                    if newcoord not in allcoords:
                        coords.append(newcoord)
                        allcoords.append(newcoord)
                    newcoord = str(latround) + ',' + str(lnground - 0.03)
                    if newcoord not in allcoords:
                        coords.append(newcoord)
                        allcoords.append(newcoord)
                    newcoord = str(latround) + ',' + str(lnground + 0.03)
                    if newcoord not in allcoords:
                        coords.append(newcoord)
                        allcoords.append(newcoord)
                    newcoord = str(latround - 0.03) + ',' + str(lnground)
                    if newcoord not in allcoords:
                        coords.append(newcoord)
                        allcoords.append(newcoord)
                    newcoord = str(latround - 0.03) + ',' + str(lnground + 0.03)
                    if newcoord not in allcoords:
                        coords.append(newcoord)
                        allcoords.append(newcoord)
                    newcoord = str(latround - 0.03) + ',' + str(lnground - 0.03)
                    if newcoord not in allcoords:
                        coords.append(newcoord)
                        allcoords.append(newcoord)
            except:
                PageFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
