import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lvhn_org')



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
    cats = []
    alllocs = []
    donelocs = []
    url = 'https://www.lvhn.org/locations?radius=20037.5&zip=10002&sort_by=search_api_relevance&sort_order=DESC&region=All&location%5Bdistance%5D%5Bfrom%5D=20037.5&location%5Bvalue%5D=10002'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<select data-drupal-selector="edit-location-types"' in line:
            items = line.split('</option><option value="')
            for item in items:
                if 'All Locations -' not in item:
                    catnum = item.split('"')[0]
                    catname = item.split('">')[1].split('<')[0].replace('&#039;',"'")
                    cats.append(catnum + '|' + catname)
    for cat in cats:
        url2 = 'https://www.lvhn.org/locations?radius=20037.5&zip=10002&sort_by=search_api_relevance&sort_order=DESC&location_types=' + cat.split('|')[0] + '&region=All&location%5Bdistance%5D%5Bfrom%5D=20037.5&location%5Bvalue%5D=10002'
        catname = cat.split('|')[1]
        pagenum = 0
        Found = True
        while Found:
            urlloc = url2 + '&page=' + str(pagenum)
            pagenum = pagenum + 1
            logger.info(('Pulling Category %s, %s...' % (catname, str(pagenum))))
            Found = False
            r2 = session.get(urlloc, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            for line2 in r2.iter_lines(decode_unicode=True):
                if 'NEXT</span>' in line2:
                    Found = True
                if '<a href="/locations/' in line2 and '<div class="field__item">' not in line2:
                    lurl = 'https://www.lvhn.org' + line2.split('<a href="')[1].split('"')[0]
                    alllocs.append(lurl)
                    locs.append(lurl + '|' + catname)
    pagenum = 0
    PFound = True
    while PFound:
        if pagenum == 44:
            pagenum = pagenum + 1
        urlnew = 'https://www.lvhn.org/locations?radius=20037.5&zip=10002&sort_by=search_api_relevance&sort_order=DESC&region=All&location%5Bdistance%5D%5Bfrom%5D=20037.5&location%5Bvalue%5D=10002&keys=&location_types=All&physician_practice=All&services=All&page=' + str(pagenum)
        pagenum = pagenum + 1
        PFound = False
        logger.info(('Pulling Full List Page %s...' % str(pagenum)))
        r2 = session.get(urlnew, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'NEXT</span>' in line2:
                PFound = True
            if '<a href="/locations/' in line2 and '<div class="field__item">' not in line2:
                lurl = 'https://www.lvhn.org' + line2.split('<a href="')[1].split('"')[0]
                if lurl not in alllocs:
                    alllocs.append(lurl)
                    locs.append('https://www.lvhn.org' + line2.split('<a href="')[1].split('"')[0] + '|<MISSING>')
        logger.info(('%s Locations Found...' % str(len(locs))))
    for loc in locs:
        lurl = loc.split('|')[0]
        typ = loc.split('|')[1]
        logger.info(('Pulling Location %s...' % lurl))
        website = 'lvhn.org'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = '<MISSING>'
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(lurl, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if name == '' and '<title>' in line2:
                name = line2.split('<title>')[1].split(' |')[0]
            if '"address-line1">' in line2:
                add = line2.split('"address-line1">')[1].split('<')[0]
            if 'class="locality">' in line2:
                city = line2.split('class="locality">')[1].split('<')[0]
            if '"administrative-area">' in line2:
                state = line2.split('"administrative-area">')[1].split('<')[0]
            if '="postal-code">' in line2:
                zc = line2.split('="postal-code">')[1].split('<')[0]
            if '<div class="field__item"><a href="tel:' in line2:
                phone = line2.split('<div class="field__item"><a href="tel:')[1].split('"')[0]
            if '"geo": "POINT (' in line2:
                lng = line2.split('"geo": "POINT (')[1].split(' ')[0]
                lat = line2.split(')')[0].rsplit(' ',1)[1]
            if '<td class="office-hours__item-label">' in line2:
                hrs = line2.split('<td class="office-hours__item-label">')[1].split('<')[0]
            if '<td class="office-hours__item-slots">' in line2:
                hrs = hrs + line2.split('<td class="office-hours__item-slots">')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if ' Suite' in add:
            add = add.split(' Suite')[0]
        if ' #' in add:
            add = add.split(' #')[0]
        if lurl not in donelocs:
            donelocs.append(lurl)
            yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
