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
    url = 'https://www.selectmedical.com//sxa/search/results/?s={648F4C3A-C9EA-4FCF-82A3-39ED2AC90A06}&itemid={94793D6A-7CC7-4A8E-AF41-2FB3EC154E1C}&sig=&autoFireSearch=true&v={D2D3D65E-3A18-43DD-890F-1328E992446A}&p=200&e=0'
    r = session.get(url, headers=headers)
    count = 0
    for line in r.iter_lines():
        if '"Count":' in line:
            count = int(line.split('"Count":')[1].split(',')[0])
    for x in range(0, count + 200, 200):
        print('Pulling Results %s...' % str(x))
        url2 = 'https://www.selectmedical.com//sxa/search/results/?s={648F4C3A-C9EA-4FCF-82A3-39ED2AC90A06}&itemid={94793D6A-7CC7-4A8E-AF41-2FB3EC154E1C}&sig=&autoFireSearch=true&v={D2D3D65E-3A18-43DD-890F-1328E992446A}&p=200&e=' + str(x)
        r2 = session.get(url2, headers=headers)
        for line2 in r2.iter_lines():
            if '"Id":"' in line2:
                items = line2.split('"Id":"')
                for item in items:
                    if '"Language":"e' in item:
                        website = 'selectmedical.com'
                        name = item.split('data-variantfieldname=\\"Link')[1].split('>')[1].split('<')[0]
                        add = item.split('address field-address\\">')[1].split('<')[0]
                        city = item.split('city field-city\\">')[1].split('<')[0]
                        state = item.split('state field-state\\">')[1].split('<')[0]
                        zc = item.split('zip field-zip\\">')[1].split('<')[0]
                        phone = item.split('"phone-container\\"><div><a href=\\"tel:')[1].split('"')[0].replace('/','').replace('\\','')
                        hours = '<MISSING>'
                        country = 'US'
                        typ = item.split('\\"line-of-business\\">')[1].split('<')[0]
                        store = item.split('"')[0]
                        lat = item.split('data-latlong=\\"')[1].split('|')[0]
                        lng = item.split('data-latlong=\\"')[1].split('|')[1].split('\\')[0]
                        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
