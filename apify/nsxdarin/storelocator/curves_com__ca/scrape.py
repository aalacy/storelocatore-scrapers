import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('curves_com__ca')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'cookie': '__cfduid=d21407db978f6fedfbb877d44bdf3a76c1595344274; _gcl_au=1.1.1927393316.1595344271; _ga=GA1.2.940401805.1595344271; _fbp=fb.1.1595344271687.1837991533; _icl_user_selected_region=ca; _icl_current_language=ca; wp-wpml_current_language=ca; _gid=GA1.2.2064215765.1595601197; _uetsid=b5ddfc3bde6274a8680d6c0406ffe280; _uetvid=c9edbf0d746722fd7ddf3cc4bc1c6708'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    canada = ['ON','SK','YT','PEI','PE','NB','NL','NS','AB','MB','BC','QC','NV','NU','NT']
    for xlat in range(44, 70):
        for ylng in range(-80, -52):
            url = 'https://www.curves.com/ca/find-a-club?location=Toronto,%20ON&lat=' + str(xlat) + '&lng=' + str(ylng)
            logger.info(url)
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                line = str(line.decode('utf-8'))
                if '>&#x1F4DE;</i>' in line:
                    phone = line.split('>&#x1F4DE;</i>')[1].split('<')[0]
                if '<a href="https://www.wellnessliving.com' in line:
                    purl = line.split('href="')[1].split('"')[0]
                    logger.info(purl)
                    if purl not in ids:
                        ids.append(purl)
                        r2 = session.get(purl, headers=headers)
                        logger.info('Pulling Location %s...' % purl)
                        name = ''
                        website = 'curves.com'
                        typ = 'Fitness Studio'
                        add = ''
                        city = ''
                        state = ''
                        zc = ''
                        country = 'CA'
                        store = '<MISSING>'
                        lat = ''
                        lng = ''
                        hours = ''
                        for line2 in r2.iter_lines():
                            line2 = str(line2.decode('utf-8'))
                            if '<meta name="geo.position" content="' in line2:
                                lat = line2.split('<meta name="geo.position" content="')[1].split(';')[0]
                                lng = line2.split('<meta name="geo.position" content="')[1].split(';')[1].split('"')[0]
                            if '"geo.placename" content="' in line2:
                                name = line2.split('"geo.placename" content="')[1].split('"')[0]
                            if 'margin:0;">  <li> <img alt="' in line2:
                                typ = line2.split('margin:0;">  <li> <img alt="')[1].split(' in ')[0]
                            if '<span itemprop="streetAddress">' in line2:
                                add = line2.split('<span itemprop="streetAddress">')[1].split('<')[0]
                                city = line2.split('itemprop="addressLocality">')[1].split('<')[0]
                                state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
                                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
                            if 'class="rs-microsite-right-day-column"><span>' in line2:
                                alldays = []
                                allhrs = []
                                days = line2.split('right-day-column">')[1].split('<br /></div>')[0].split('<br />')
                                for day in days:
                                    if '</span>' in day:
                                        dname = day.rsplit('>')[1].split('<')[0]
                                        alldays.append(dname)
                                hrs = line2.split('right-time-column">')[1].split('<br /></div>')[0].split('<br />')
                                for hour in hrs:
                                    if '</span>' in hour:
                                        if hour.count('</span>') == 1:
                                            allhrs.append(hour.split('>')[1].split('<')[0])
                                        else:
                                            allhrs.append(hour.split('</span>')[1])
                                for x in range(0, len(alldays)):
                                    if hours == '':
                                        hours = alldays[x] + ': ' + allhrs[x]
                                    else:
                                        hours = hours + '; ' + alldays[x] + ': ' + allhrs[x]
                        if hours == '':
                            hours = '<MISSING>'
                        if phone == '':
                            phone = '<MISSING>'
                        if add != '' and state in canada:
                            yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
