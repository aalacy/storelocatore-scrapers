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
    url = 'https://www.pink-barre.com/locations'
    r = session.get(url, headers=headers)
    website = 'pink-barre.com'
    typ = '<MISSING>'
    country = 'US'
    store = '<MISSING>'
    hours = ''
    lat = '<MISSING>'
    lng = '<MISSING>'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '&amp;sLoc=0">' in line:
            items = line.split('&amp;sLoc=0">')
            for item in items:
                 if '</a></h2>' in item:
                     name = item.split('<')[0]
                     loc = 'https://clients.mindbodyonline.com/ASP/su1.asp?studioid=42111&tg=&vt=&lvl=&stype=-7&view=day&trn=0&page=&catid=&prodid=&date=7%2f10%2f2020&classid=0&prodGroupId=&sSU=&optForwardingLink=&qParam=&justloggedin=&nLgIn=&pMode=0'
                     add = item.split('<em>')[1].split('<')[0]
                     city = item.split('</em><br>')[1].split(',')[0]
                     state = item.split('</em><br>')[1].split(',')[1].strip().split(' ')[0]
                     zc = item.split('</em><br>')[1].split('<')[0].rsplit(' ',1)[1]
                     phone = item.split('<strong>')[1].split('<')[0]
                     hours = item.split('please call between:')[1].split('@')[0].replace('</p>','').replace('<p style="text-align:right;white-space:pre-wrap;" class="">','').replace('<p class="" style="white-space:pre-wrap;">','').strip().replace('&amp;','&')
                     hours = hours.replace('vahi','').replace('buckhead','').replace('Saturday','; Saturday')
                     yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
