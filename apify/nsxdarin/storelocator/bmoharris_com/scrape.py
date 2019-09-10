import csv
import urllib2
import requests
import gzip
import os

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
    smurl = 'https://branches.bmoharris.com/sitemap.xml.gz'
    with open('branches.xml.gz','wb') as f:
        f.write(urllib2.urlopen(smurl).read())
        f.close()

    print('Branch List Downloaded...')
    branches = []
    stores = []
    ids = []
    with gzip.open('branches.xml.gz', 'rb') as f:
        for line in f:
            if '/harris1' in line or '/harris2' in line:
                burl = line.split('>')[1].split('<')[0]
                bid = burl.rsplit('/harris',1)[1]
                if bid not in ids:
                    ids.append(bid)
                    branches.append(burl)

    os.remove("branches.xml.gz")
    print('Found %s Branches.' % str(len(branches)))
    
    for branch in branches:
        website = 'bmoharris.com'
        typ = 'Branch'
        hours = '<MISSING>'
        Found = False
        while Found is False:
            Found = True
            try:
                print('Pulling Branch %s...' % branch)
                r = session.get(branch, headers=headers, timeout=10)
                lines = r.iter_lines()
                for line in lines:
                    if 'property="og:title" content="' in line:
                        name = line.split('property="og:title" content="')[1].split('"')[0]
                    if '"streetAddress":"' in line:
                        add = line.split('"streetAddress":"')[1].split('"')[0]
                    if '"addressLocality":"' in line:
                        city = line.split('"addressLocality":"')[1].split('"')[0]
                    if '"addressRegion":"' in line:
                        state = line.split('"addressRegion":"')[1].split('"')[0]
                    if '"postalCode":"' in line:
                        zc = line.split('"postalCode":"')[1].split('"')[0]
                    if '"latitude":' in line:
                        lat = line.split('"latitude":')[1].split(',')[0]
                    if '"longitude":' in line:
                        lng = line.split('"longitude":')[1].strip().replace('\r','').replace('\n','')
                    if '"addressCountry":"' in line:
                        country = line.split('"addressCountry":"')[1].split('"')[0]
                    if '"@id":"' in line:
                        store = line.split('"@id":"')[1].split('"')[0].replace('harris','')
                    if '"telephone":"' in line:
                        phone = line.split('"telephone":"')[1].split('"')[0]
                    if '"dayOfWeek":[' in line:
                        g = next(lines)
                        next(lines)
                        o = next(lines)
                        c = next(lines)
                        day = g.split('"')[1]
                        ophr = o.split('":"')[1].split('"')[0]
                        clhr = c.split('":"')[1].split('"')[0]
                        if hours == '<MISSING>':
                            hours = day + ': ' + ophr + '-' + clhr
                        else:
                            hours = hours + '; ' + day + ': ' + ophr + '-' + clhr
                    if '</html>' in line:
                        if store not in stores:
                            stores.append(store)
                            hours = hours.replace('closed-closed','closed')
                            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                Found = False

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
