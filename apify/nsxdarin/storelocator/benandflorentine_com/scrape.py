import csv
import urllib2
import requests

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://benandflorentine.com/locations/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '"cssClass":" ouvert-en' in line:
            line = line.replace('"categories":[{"title":"','---')
            items = line.split('{"title":"')
            for item in items:
                if '"simpledescription":"' in item:
                    website = 'benandflorentine.com'
                    name = item.split('"')[0]
                    add = item.split('"address":"<p>')[1].split('<')[0]
                    try:
                        city = item.split('"address":"<p>')[1].split('<br \\/>\\n')[1].split(',')[0].strip()
                    except:
                        city = item.split('"address":"<p>')[1].split(',')[2].strip()
                    try:
                        state = item.split('"address":"<p>')[1].split('<br \\/>\\n')[1].split(',')[1].strip()
                    except:
                        state = item.split('"address":"<p>')[1].split(',')[3].strip()
                    if '<' in state:
                        state = state.split('<')[0].strip()
                    if ' ' in state:
                        zc = state.split(' ',1)[1]
                        state = state.split(' ')[0]
                    else:
                        try:
                            zc = item.split('"address":"<p>')[1].split('<br \\/>\\n')[1].split('<')[0].split(',')[2]
                        except:
                            zc = '<MISSING>'
                    if len(state) > 2:
                        state = '<MISSING>'
                    state = state.strip()
                    zc = zc.strip()
                    city = city.strip()
                    add = add.strip()
                    if zc == '0H3':
                        zc = 'H7E 0H3'
                    phone = item.split("<a href='tel:")[1].split("'")[0].replace('.','-')
                    hours = item.split('<br><hr><br>')[2].split('<\\/span')[0].replace('<br \\/>\\r\\n','; ')
                    country = 'CA'
                    typ = 'Restaurant'
                    store = item.split('loc-')[1].split('"')[0]
                    lat = item.split('"latitude":"')[1].split('"')[0]
                    lng = item.split('"longitude":"')[1].split('"')[0]
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
