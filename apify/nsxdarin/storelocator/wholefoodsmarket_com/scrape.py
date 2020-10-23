import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('wholefoodsmarket_com')



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
    urls = ['https://www.wholefoodsmarket.com/sitemap/sitemap-stores.xml']
    locs = []
    for url in urls:
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '<loc>https://www.wholefoodsmarket.com/stores/' in line:
                items = line.split('<loc>')
                for item in items:
                    if 'https://www.wholefoodsmarket.com/stores/' in item:
                        lurl = item.split('<')[0]
                        locs.append(lurl)
    logger.info(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        url = loc
        add = ''
        city = ''
        state = ''
        zc = ''
        country = ''
        phone = ''
        hours = ''
        store = '<MISSING>'
        name = 'Whole Foods Market'
        website = 'wholefoodsmarket.com'
        typ = 'Store'
        today = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0].split(' |')[0]
            if "<span class='w-mailing-address-section--description-first'>" in line2:
                add = line2.split("<span class='w-mailing-address-section--description-first'>")[1].split('<')[0]
                csz = line2.split("<span class='w-mailing-address-section--description-last'>")[1].split('<')[0]
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.split(',')[1].strip().split(' ',1)[1]
                if ' ' in zc:
                    country = 'CA'
                else:
                    country = 'US'
            if 'class="w-phone-number--link ">' in line2:
                phone = line2.split('class="w-phone-number--link ">')[1].split('<')[0]
            if '<img class="w-map" src=' in line2:
                lat = line2.split('%7C')[1].split(',')[0]
                lng = line2.split('%7C')[1].split(',')[1].split('&')[0]
            if '<div class= "w-hours-of-operation--store-day w-body-short-form-bold">' in line2:
                hours = line2.split('<div class= "w-hours-of-operation--store-hours w-body-short-form">')[1].split('<')[0]
            if '<div class= "w-hours-of-operation--store-day w-body-short-form">' in line2:
                days = line2.split('<div class= "w-hours-of-operation--store-day w-body-short-form">')
                for day in days:
                    if ':</div><div class= "w-hours' in day:
                        hrs = day.split('<')[0] + ' ' + day.split('form">')[1].split('<')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs                
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if state == 'BC' or state == 'QC' or state == 'ON':
            country = 'CA'
        if add != '':
            yield [website, url, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        url = 'https://www.wholefoodsmarket.com/stores/search'
    locs = []
    payload = {"query":["AYAAFOedDKENmOaaURfqtV/zEcEALgACABFvcmlnaW5hbEZpZWxkTmFtZQAFcXVlcnkADWZyYWdtZW50SW5kZXgAATAAAQAGc2k6bWQ1ACBjNjEyNzMwZmM4NzA0NjYyMThkZjRiMjc1YWFlYTJiNQEAPOhlmJP1EnDxvtOvSd/ckG4EsKlX24HCJ7Ytx3ux444C2PXDzX7c7phhh4FfMD5W0S8cxCexDiP16Ktn2O/1xluzhIpEQt9LPaHN0YEZ+oxPsVrCfn0JR+dXhDbxYePMZO9HHIZR/vm6r3TDdlYC9iuOPSY2E0rk8mt8gZnZGb/ueYVWjJKWzjo3vA9qN0q/fQCSekPuUSlLBnOx1sI3XFIBfeujCmmjYbgGNw8TnTd2KCrjYH3YPiktRiw+3mdUDc+pl9/xgwGDzATnhAGXFwHq5oKqTRlhQzldXD0L7gHGdZ4DR96TYiLJawqT7i7Z5W5V9Goh0wbl38NwYx7fHgIAAAAADAAAACgAAAAAAAAAAAAAAACgxENGGAexhATiEb63DF0q/////wAAAAEAAAAAAAAAAAAAAAEAAAAn4cvNgh6oSjxx/LVXtdlqbeBEbM96hs3pDrdUmPy2ESLs9muar7gFxTskKozaFVwGji7wHjw6lA=="]}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '"folder":"' in line:
            items = line.split('"folder":"')
            for item in items:
                if '"links":' in item:
                    lurl = 'https://www.wholefoodsmarket.com/stores/' + item.split('"')[0]
                    locs.append(lurl)
    logger.info(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        url = loc
        add = ''
        city = ''
        state = ''
        zc = ''
        country = ''
        phone = ''
        hours = ''
        store = '<MISSING>'
        name = 'Whole Foods Market'
        website = 'wholefoodsmarket.com'
        typ = 'Store'
        today = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0].split(' |')[0]
            if "<span class='w-mailing-address-section--description-first'>" in line2:
                add = line2.split("<span class='w-mailing-address-section--description-first'>")[1].split('<')[0]
                csz = line2.split("<span class='w-mailing-address-section--description-last'>")[1].split('<')[0]
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.split(',')[1].strip().split(' ',1)[1]
                if ' ' in zc:
                    country = 'CA'
                else:
                    country = 'US'
            if 'class="w-phone-number--link ">' in line2:
                phone = line2.split('class="w-phone-number--link ">')[1].split('<')[0]
            if '<img class="w-map" src=' in line2:
                lat = line2.split('%7C')[1].split(',')[0]
                lng = line2.split('%7C')[1].split(',')[1].split('&')[0]
            if '<div class= "w-hours-of-operation--store-day w-body-short-form-bold">' in line2:
                hours = line2.split('<div class= "w-hours-of-operation--store-hours w-body-short-form">')[1].split('<')[0]
            if '<div class= "w-hours-of-operation--store-day w-body-short-form">' in line2:
                days = line2.split('<div class= "w-hours-of-operation--store-day w-body-short-form">')
                for day in days:
                    if ':</div><div class= "w-hours' in day:
                        hrs = day.split('<')[0] + ' ' + day.split('form">')[1].split('<')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs                
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if state == 'BC' or state == 'QC' or state == 'ON':
            country = 'CA'
        if add != '':
            yield [website, url, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

    locs = []
    url = 'https://www.wholefoodsmarket.com/stores/search'
    payload = {"query":["AYAAFGL2ZAEAPAhMuUj8IuW/owoALgACABFvcmlnaW5hbEZpZWxkTmFtZQAFcXVlcnkADWZyYWdtZW50SW5kZXgAATAAAQAGc2k6bWQ1ACBjNjEyNzMwZmM4NzA0NjYyMThkZjRiMjc1YWFlYTJiNQEAg+PlV4FRWbsLb6xespRkxrgYZoCeg+UlMylHN+jcwD4DKfeYwyK4lkEWrBemaZE74yP6K2RFRCr+0wpI2CNiC/Bx/al+68grySF3gv7rykiDYndrU8jUwtuTqjvXThn0w2VwPhozbO15gSdzF/Y8ISXX4qp3K9igJUDILVfZxLGfBgDajXOBXcVVT5Kw+n+pZQ2Wkw7yJrKtFsfLRQs5fglcW/fOhiUVPKChU2RwM4cWpZvF7GGQHOfXvm0doMgR6KquAuC+C2WT+joZETULmuqi8j6QmterbNCVBlXNw9DEfBUWDWpW+4RzMNTDE/H4l5aJIuFdZ77836ObCykO5wIAAAAADAAAACYAAAAAAAAAAAAAAADhSaBmdH/7ltQeK6mPU2+I/////wAAAAEAAAAAAAAAAAAAAAEAAAAlWJMmVBTnHghLMxhdKUdWDuye5KRsIAVmqJpjA+DYnb4pnHYEONsZ4BPn8TYs2Qya4FUcPTw="]}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '"folder":"' in line:
            items = line.split('"folder":"')
            for item in items:
                if '"links":' in item:
                    lurl = 'https://www.wholefoodsmarket.com/stores/' + item.split('"')[0]
                    locs.append(lurl)
    logger.info(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        url = loc
        add = ''
        city = ''
        state = ''
        zc = ''
        country = ''
        phone = ''
        hours = ''
        store = '<MISSING>'
        name = 'Whole Foods Market'
        website = 'wholefoodsmarket.com'
        typ = 'Store'
        today = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0].split(' |')[0]
            if "<span class='w-mailing-address-section--description-first'>" in line2:
                add = line2.split("<span class='w-mailing-address-section--description-first'>")[1].split('<')[0]
                csz = line2.split("<span class='w-mailing-address-section--description-last'>")[1].split('<')[0]
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.split(',')[1].strip().split(' ',1)[1]
                if ' ' in zc:
                    country = 'CA'
                else:
                    country = 'US'
            if 'class="w-phone-number--link ">' in line2:
                phone = line2.split('class="w-phone-number--link ">')[1].split('<')[0]
            if '<img class="w-map" src=' in line2:
                lat = line2.split('%7C')[1].split(',')[0]
                lng = line2.split('%7C')[1].split(',')[1].split('&')[0]
            if '<div class= "w-hours-of-operation--store-day w-body-short-form-bold">' in line2:
                hours = line2.split('<div class= "w-hours-of-operation--store-hours w-body-short-form">')[1].split('<')[0]
            if '<div class= "w-hours-of-operation--store-day w-body-short-form">' in line2:
                days = line2.split('<div class= "w-hours-of-operation--store-day w-body-short-form">')
                for day in days:
                    if ':</div><div class= "w-hours' in day:
                        hrs = day.split('<')[0] + ' ' + day.split('form">')[1].split('<')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs                

        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if state == 'BC' or state == 'QC' or state == 'ON':
            country = 'CA'
        if add != '':
            yield [website, url, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
