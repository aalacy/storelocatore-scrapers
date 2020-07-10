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
    url = 'https://redlandsgrill.com/locations/'
    r = session.get(url, headers=headers)
    website = 'redlandsgrill.com'
    typ = '<MISSING>'
    store = '<MISSING>'
    country = 'US'
    loc = 'redlandsgrill.com/locations/'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if 'pm<' in line and '<div class="socialMediaLinks">' not in line:
            hrs = line.split('<')[0]
            if hours == '':
                hours = hrs
            else:
                hours = hours + '; ' + hrs
        if 'pm<' in line and '<div class="socialMediaLinks">' in line:
            hrs = line.split('<')[0]
            if hours == '':
                hours = hrs
            else:
                hours = hours + '; ' + hrs
            if '<div class="socialMediaLinks">' in line and name != '':
                if 'Cincinnati' in name:
                    hours = 'Mon-Sun 11:30am-11pm'
                if 'Peachtree' in name:
                    hours = 'Sun-Thurs: 11am-9pm; Fri-Sat: 11am-10pm'
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            if '<h4>Redlands Grill' not in line:
                name = ''
        if '<h4>Redlands Grill | ' in line:
            name = line.split('<h4>')[1].split('<')[0]
            hours = ''
        if '<address>' in line:
            if 'Hours of Operation<br /><p>' in line and 'Hours of Operation<br /><p><!' not in line:
                hrs = line.split('Hours of Operation<br /><p>')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            addinfo = line.split('<address>')[1].split('</a>')[0]
            phone = line.split('<a href="tel:')[1].split('"')[0]
            if addinfo.count('<br />') == 2:
                add = addinfo.split('<br />')[0] + ' ' + addinfo.split('<br />')[1]
                city = addinfo.split('<br />')[2].split(',')[0]
                state = addinfo.split('<br />')[2].split(',')[1].strip().rsplit(' ',1)[0]
                zc = addinfo.rsplit(' ',1)[1]
            else:
                add = addinfo.split('<br />')[0]
                city = addinfo.split('<br />')[1].split(',')[0]
                state = addinfo.split('<br />')[1].split(',')[1].strip().rsplit(' ',1)[0]
                zc = addinfo.rsplit(' ',1)[1]
        if '/@' in line:
            lat = line.split('/@')[1].split(',')[0]
            lng = line.split('/@')[1].split(',')[1]
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
