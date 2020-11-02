import csv
import urllib.request, urllib.error, urllib.parse
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
    url = 'https://www.spinpizza.com/locations/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    website = 'spinpizza.com'
    typ = '<MISSING>'
    country = 'US'
    loc = '<MISSING>'
    store = '<MISSING>'
    hours = ''
    lat = ''
    lng = ''
    LFound = False
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if '<div class="location" id="' in line:
            store = line.split('<div class="location" id="')[1].split('"')[0]
        if '><strong>SPIN!' in line:
            name = line.split('<strong>')[1].split('<')[0]
            loc = 'https://www.spinpizza.com/' + line.split('href="')[1].split('"')[0]
        if '<div class="add">' in line:
            g = next(lines)
            if g.count('<br/>') == 4:
                add = g.split('<br/>')[0].strip().replace('\t','') + ' ' + g.split('<br/>')[1]
                city = g.split('<br/>')[2].split(',')[0]
                state = g.split('<br/>')[2].split(',')[1].strip()
                zc = g.split('<br/>')[3]
                phone = g.split('<br/>')[4].strip()
            else:
                try:
                    add = g.split('<br/>')[0].strip().replace('\t','')
                    city = g.split('<br/>')[1].split(',')[0]
                    state = g.split('<br/>')[1].split(',')[1].strip()
                    zc = g.split('<br/>')[2]
                    phone = g.split('<br/>')[3].strip()
                except:
                    add = ''
        if 'HOURS<br/>' in line:
            hours = line.split('HOURS<br/>')[1].replace('<br/>\r','').replace('<br/>\n','').strip().replace('<br/>','; ')
            locs.append(store + '|' + loc + '|' + name + '|' + add + '|' + city + '|' + state + '|' + zc + '|' + phone + '|' + hours)
        if 'var locations = [' in line:
            LFound = True
        if LFound and '];' in line:
            LFound = False
        if LFound and ']' in line:
            line = line.replace('"',"'")
            sid = line.split("','")[1].split("'")[0]
            lat = line.split("','")[1].split(',')[1]
            lng = line.split("','")[1].split(',')[2].split(']')[0]
            for litem in locs:
                if sid == litem.split('|')[0]:
                    store = sid
                    loc = litem.split('|')[1]
                    name = litem.split('|')[2]
                    add = litem.split('|')[3]
                    city = litem.split('|')[4]
                    state = litem.split('|')[5]
                    zc = litem.split('|')[6]
                    phone = litem.split('|')[7]
                    hours = litem.split('|')[8]
                    hours = hours.replace('<Br/>','; ').replace('-->','')
                    add = add.replace('<!--','').strip().replace('\t','')
                    if hours[-2:] == '; ':
                        hours = hours[:-2]
                    phone = phone.replace('-->','')
                    if add != '':
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
