import csv
import urllib2
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
    scalocs = []
    mtlocs = []
    aklocs = []
    orlocs = []
    walocs = []
    Found = False
    for x in range(1, 15):
        print('Pulling WA Page %s...' % str(x))
        url = 'https://washington.providence.org/locations-directory/search-results?page=' + str(x)
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<ul  class="list-unstyled row">' in line:
                Found = True
            if Found and '<div id="psjh_body_1' in line:
                Found = False
            if Found and '<a href="/locations-directory/' in line:
                lurl = 'https://washington.providence.org' + line.split('href="')[1].split('"')[0]
                if lurl not in walocs:
                    walocs.append(lurl)
        print('%s WA Locations Found' % str(len(walocs)))
    for loc in walocs:
        HFound = False
        print('Pulling WA Location %s...' % loc)
        website = 'providence.org'
        typ = '<MISSING>'
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
        r = session.get(loc, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            if '<title>' in line:
                g = next(lines)
                name = g.split(' |')[0].strip().replace('\t','')
            if 'locationHoursContainer_0">' in line:
                HFound = True
            if HFound and '</div>' in line:
                HFound = False
            if HFound and 'day,' in line and '<p>' in line:
                hrs = line.split('<p>')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if HFound and 'day:' in line and '<p>' in line:
                hrs = line.split('<p>')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if HFound and '<br />' in line:
                if 'p.m' in line:
                    hrs = line.split('<br />')[0]
                    if hours == '':
                        hours = hrs
                    else:
                        hours = hours + '; ' + hrs
                else:
                    g = line
                    h = next(lines)
                    if 'p.m' in h:
                        hrs = g.split('<br')[0] + ': ' + h.strip().replace('\r','').replace('\t','').replace('\n','')
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
                hours = hours.replace('&nbsp;',' ')
                hours = hours.replace('  ',' ')
            if 'addressContainer_0">' in line:
                g = next(lines)
                h = next(lines)
                add = g.strip().replace('\r','').replace('\t','').replace('\n','')
                csz = h.strip().replace('\r','').replace('\t','').replace('\n','')
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.rsplit(' ',1)[1]
            if '<a href="tel:' in line:
                phone = line.split('<a href="tel:')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        hours = hours.replace('&nbsp;',' ')
        if phone == '':
            phone = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        if ',' in add:
            add = add.split(',')[0].strip()
        if ' Suite' in add:
            add = add.split(' Suite')[0]
        if '; ; <a href=""' in hours:
            hours = hours.split('; ; <a href=""')[0]
        hours = hours.strip().replace('\t','').replace('&ndash;','-').replace('<p>','')
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    for x in range(1, 10):
        print('Pulling MT Page %s...' % str(x))
        url = 'https://montana.providence.org/locations-directory/list-view?page=' + str(x)
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<ul  class="list-unstyled row">' in line:
                Found = True
            if Found and '<div id="psjh_body_1' in line:
                Found = False
            if Found and '<a href="/locations-directory/' in line:
                lurl = 'https://montana.providence.org' + line.split('href="')[1].split('"')[0]
                if lurl not in mtlocs:
                    mtlocs.append(lurl)
        print('%s MT Locations Found' % str(len(mtlocs)))
    for loc in mtlocs:
        HFound = False
        print('Pulling MT Location %s...' % loc)
        website = 'providence.org'
        typ = '<MISSING>'
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
        r = session.get(loc, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            if 'locationHoursContainer_0">' in line:
                HFound = True
            if HFound and '</div>' in line:
                HFound = False
            if HFound and '<br />' in line:
                if 'p.m' in line:
                    hrs = line.split('<br />')[0]
                    if hours == '':
                        hours = hrs
                    else:
                        hours = hours + '; ' + hrs
                else:
                    g = line
                    h = next(lines)
                    if 'p.m' in h:
                        hrs = g.split('<br')[0] + ': ' + h.strip().replace('\r','').replace('\t','').replace('\n','')
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
                hours = hours.replace('&nbsp;',' ')
                hours = hours.replace('  ',' ')
            if "</span></a></li><li class='active'>" in line:
                name = line.split("</span></a></li><li class='active'>")[1].split('<')[0]
            if 'addressContainer_0">' in line:
                g = next(lines)
                h = next(lines)
                add = g.strip().replace('\r','').replace('\t','').replace('\n','')
                csz = h.strip().replace('\r','').replace('\t','').replace('\n','')
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.rsplit(' ',1)[1]
            if '<a href="tel:' in line:
                phone = line.split('<a href="tel:')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        if ',' in add:
            add = add.split(',')[0].strip()
        if ' Suite' in add:
            add = add.split(' Suite')[0]
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    for x in range(1, 50):
        print('Pulling OR Page %s...' % str(x))
        url = 'https://oregon.providence.org/location-directory/list-view/?page=' + str(x) + '&within=5000'
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<h4><a id="main_0' in line:
                lurl = 'https://oregon.providence.org' + line.split('href="')[1].split('"')[0]
                if lurl not in orlocs:
                    orlocs.append(lurl)
        print('%s OR Locations Found' % str(len(orlocs)))
    for loc in orlocs:
        print('Pulling OR Location %s...' % loc)
        website = 'providence.org'
        typ = '<MISSING>'
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
        HFound = False
        r = session.get(loc, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            if '<a id="main_0_leftpanel_0_hlNavTitle"' in line:
                name = line.split('">')[1].split('<')[0]
            if '0_pnlAddress">' in line:
                next(lines)
                g = next(lines)
                addinfo = g.strip().replace('\r','').replace('\t','').replace('\n','')
                if '<' not in addinfo:
                    addinfo = next(lines).strip().replace('\r','').replace('\t','').replace('\n','')
                if addinfo.count('<br/>') == 1:
                    add = addinfo.split('<br/>')[0]
                    city = addinfo.split('<br/>')[1].split(',')[0]
                    state = addinfo.split('<br/>')[1].split(',')[1].strip().split(' ')[0]
                    zc = addinfo.split('<br/>')[1].rsplit(' ',1)[1]
                else:
                    add = addinfo.split('<br/>')[0]
                    city = addinfo.split('<br/>')[2].split(',')[0]
                    state = addinfo.split('<br/>')[2].split(',')[1].strip().split(' ')[0]
                    zc = addinfo.split('<br/>')[2].rsplit(' ',1)[1]
            if '<a id="main_0_contentpanel_0_hlAlternatePhone"' in line:
                phone = line.split('"tel:')[1].split('"')[0]
            if '<meta itemprop="latitude" content="' in line:
                lat = line.split('<meta itemprop="latitude" content="')[1].split('"')[0]
            if '<meta itemprop="longitude" content="' in line:
                lng = line.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if 'OfficeHours">' in line:
                HFound = True
            if HFound and '<' in line and 'OfficeHours">' not in line:
                HFound = False
            if HFound and ':' in line:
                hrs = line.strip().replace('\r','').replace('\t','').replace('\n','')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if ',' in add:
            add = add.split(',')[0].strip()
        if ' Suite' in add:
            add = add.split(' Suite')[0]
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    for x in range(1, 10):
        print('Pulling AK Page %s...' % str(x))
        url = 'https://alaska.providence.org/locations/list-view?page=' + str(x) + '&within=5000'
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<h4><a id="main_0' in line:
                lurl = 'https://alaska.providence.org' + line.split('href="')[1].split('"')[0]
                if lurl not in aklocs:
                    aklocs.append(lurl)
        print('%s AK Locations Found' % str(len(aklocs)))
    for loc in aklocs:
        #print('Pulling AK Location %s...' % loc)
        website = 'providence.org'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = '<MISSING>'
        phone = ''
        lat = '<MISSING>'
        lng = '<MISSING>'
        HFound = False
        r = session.get(loc, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            if 'pnlOfficeHours">' in line:
                HFound = True
            if HFound and '</div>' in line:
                HFound = False
            if HFound and 'p.m.' in line:
                hrs = line.strip().replace('\r','').replace('\t','').replace('\n','')
                if '<' in hrs:
                    hrs = hrs.split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if HFound and 'p.m.' not in line and 'losed' in line:
                hrs = line.strip().replace('\r','').replace('\t','').replace('\n','')
                if '<' in hrs:
                    hrs = hrs.split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '<title>' in line:
                g = next(lines)
                name = g.split(' |')[0].strip().replace('\t','')
            if 'class="address">' in line or 'pnlAddress">' in line:
                next(lines)
                g = next(lines)
                addinfo = g.strip().replace('\r','').replace('\t','').replace('\n','')
                if addinfo.count('<br/>') == 1:
                    add = addinfo.split('<br/>')[0]
                    city = addinfo.split('<br/>')[1].split(',')[0]
                    state = addinfo.split('<br/>')[1].split(',')[1].strip().split(' ')[0]
                    zc = addinfo.split('<br/>')[1].rsplit(' ',1)[1]
                else:
                    add = addinfo.split('<br/>')[0]
                    city = addinfo.split('<br/>')[2].split(',')[0]
                    state = addinfo.split('<br/>')[2].split(',')[1].strip().split(' ')[0]
                    zc = addinfo.split('<br/>')[2].rsplit(' ',1)[1]
            if '<a id="main_0_rightpanel_0_hlAlternatePhone"' in line:
                phone = line.split('"tel:')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if 'n/neuroscience-center' in loc:
            add = '3851 Piper Street'
            city = 'Anchorage'
            state = 'AK'
            zc = '99508'
            phone = '907-212-5606'
        if '3801-' in loc:
            add = '3801 Lake Otis Parkway'
            city = 'Anchorage'
            state = 'AK'
            zc = '99508'
        if 'c/providence-cancer-center' in loc:
            add = '3851 Piper Street'
            state = 'AK'
            zc = '99508'
            city = 'Anchorage'
        if 'anchorage/providence-diabetes-and-nutrition-center' in loc:
            add = '3220 Providence Drive'
            city = 'Anchorage'
            state = 'AK'
            zc = '99508'
        if '/p/providence-medical-group-u-med' in loc:
            add = '3260 Providence Drive'
            city = 'Anchorage'
            state = 'AK'
            zc = '99508'
        if 'medical-group-primary-care' in loc:
            add = '3300 Providence Drive'
            city = 'Anchorage'
            state = 'AK'
            zc = '99508'
        if 'providence-rehabilitation-services' in loc:
            add = '4411 Business Park Blvd'
            city = 'Anchorage'
            state = 'AK'
            zc = '99503'
        if ',' in add:
            add = add.split(',')[0].strip()
        if ' Suite' in add:
            add = add.split(' Suite')[0]
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    for x in range(1, 75):
        print('Pulling SCA Page %s...' % str(x))
        url = 'https://www.providence.org/locations?postal=90210&lookup=&lookupvalue=&page=' + str(x) + '&radius=5000&term=#'
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<h3><a href="' in line:
                stub = line.split('a href="')[1].split('"')[0]
                if '/location' in stub and '.providence.org' not in stub:
                    lurl = 'https://www.providence.org' + stub
                    if lurl not in scalocs and lurl.count('http') == 1:
                        scalocs.append(lurl)
        print('%s SCA Locations Found' % str(len(scalocs)))
    for loc in scalocs:
        print('Pulling SCA Location %s...' % loc)
        website = 'providence.org'
        typ = '<MISSING>'
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
        r = session.get(loc, headers=headers)
        for line in r.iter_lines():
            if '"streetAddress":"' in line:
                name = line.split('"name":"')[1].split('"')[0]
                add = line.split('"streetAddress":"')[1].split('"')[0]
                city = line.split('"addressLocality":"')[1].split('"')[0]
                state = line.split('"addressRegion":"')[1].split('"')[0]
                zc = line.split('"postalCode":"')[1].split('"')[0]
                phone = line.split('"telephone":"')[1].split('"')[0]
                lat = line.split('"latitude":')[1].split(',')[0]
                lng = line.split('"longitude":')[1].split('}')[0]
                typ = line.split(',"@type":"')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if ',' in add:
            add = add.split(',')[0].strip()
        if ' Suite' in add:
            add = add.split(' Suite')[0]
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    r = session.get('https://www.stjosephhealth.org/our-locations/', headers=headers)
    lines = r.iter_lines()
    for line in lines:
        if '<div class="location">' in line:
            g = next(lines)
            if '<h3>' in g:
                typ = '<MISSING>'
                name = g.split('">')[1].split('<')[0]
            else:
                g = next(lines)
                name = g.split('>')[1].split('<')[0]
                typ = name
                if ' - ' in typ:
                    typ = typ.split(' - ')[0]
            next(lines)
            g = next(lines)
            if '<p>' not in g:
                next(lines)
            g = next(lines)
            add = g.strip().replace('\r','').replace('\t','').replace('\n','')
            g = next(lines)
            csz = g.split('<br>')[1].strip().replace('\r','').replace('\t','').replace('\n','')
            city = csz.split(',')[0]
            state = csz.split(',')[1].strip().split(' ')[0]
            zc = csz.rsplit(' ',1)[1]
            country = 'US'
            website = 'providence.org'
        if 'Phone:' in line:
            try:
                phone = line.split('tel:')[1].split('"')[0]
            except:
                phone = '<MISSING>'
            lat = '<MISSING>'
            lng = '<MISSING>'
            hours = '<MISSING>'
            loc = '<MISSING>'
            store = '<MISSING>'
            if ',' in add:
                add = add.split(',')[0].strip()
            if ' Suite' in add:
                add = add.split(' Suite')[0]
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
