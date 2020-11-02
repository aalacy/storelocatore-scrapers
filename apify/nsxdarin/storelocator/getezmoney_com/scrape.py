import csv
from sgrequests import SgRequests
import usaddress

session = SgRequests()
headers = {'content-type': 'application/x-www-form-urlencoded',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "raw_address", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.getezmoney.com/find-a-location/'
    locs = []
    payload = {'zip_code': 10002,
               'distance': 50000,
               'referral_search': 'GO'
               }
    r = session.post(url, headers=headers, data=payload)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if 'valign="top">Website</td>' in line:
            items = line.split('valign="top">Website</td>')
            for item in items:
                if '<div id="content">' not in item:
                    website = 'getezmoney.com'
                    name = item.split('<a href="')[1].split('">')[1].split('<')[0]
                    city = item.split('href="')[1].split('>')[1].split('<')[0].split(',')[0]
                    state = item.split('href="')[1].split('>')[1].split(',')[1].split('<')[0].strip()
                    try:
                        rawadd = item.split('>Address</td><td class="referral-value" valign="top">')[1].split('<')[0]
                    except:
                        rawadd = ''
                    phone = item.split('<a href="tel:')[1].split('"')[0]
                    country = 'US'
                    typ = 'Location'
                    try:
                        add = usaddress.tag(rawadd)
                        baseadd = add[0]
                        if 'AddressNumber' not in baseadd:
                            baseadd['AddressNumber'] = ''
                        if 'StreetName' not in baseadd:
                            baseadd['StreetName'] = ''
                        if 'StreetNamePostType' not in baseadd:
                            baseadd['StreetNamePostType'] = ''
                        if 'PlaceName' not in baseadd:
                            baseadd['PlaceName'] = '<INACCESSIBLE>'
                        if 'StateName' not in baseadd:
                            baseadd['StateName'] = '<INACCESSIBLE>'
                        if 'ZipCode' not in baseadd:
                            baseadd['ZipCode'] = '<INACCESSIBLE>'
                        address = add[0]['AddressNumber'] + ' ' + add[0]['StreetName'] + ' ' + add[0]['StreetNamePostType']
                        address = address.encode("ascii").decode()
                        if address == '':
                            address = '<INACCESSIBLE>'
                        #city = add[0]['PlaceName']
                        #state = add[0]['StateName']
                        zc = add[0]['ZipCode']
                    except:
                        pass
                    
                    lat = '<MISSING>'
                    lng = '<MISSING>'
                    store = '<MISSING>'
                    address = address.strip().replace('\t','')
                    hours = 'Mon: ' + item.split('<td>Monday</td><td>')[1].split('</tr>')[0].replace('</td><td>','-').replace('</td>','')
                    hours = hours + '; Tue: ' + item.split('<td>Tuesday</td><td>')[1].split('</tr>')[0].replace('</td><td>','-').replace('</td>','')
                    hours = hours + '; Wed: ' + item.split('<td>Wednesday</td><td>')[1].split('</tr>')[0].replace('</td><td>','-').replace('</td>','')
                    hours = hours + '; Thu: ' + item.split('<td>Thursday</td><td>')[1].split('</tr>')[0].replace('</td><td>','-').replace('</td>','')
                    hours = hours + '; Fri: ' + item.split('<td>Friday</td><td>')[1].split('</tr>')[0].replace('</td><td>','-').replace('</td>','')
                    hours = hours + '; Sat: ' + item.split('<td>Saturday</td><td>')[1].split('</tr>')[0].replace('</td><td>','-').replace('</td>','')
                    hours = hours + '; Sun: ' + item.split('<td>Sunday</td><td>')[1].split('</tr>')[0].replace('</td><td>','-').replace('</td>','')
                    if address == '':
                        address = '<MISSING>'
                    if rawadd == '':
                        rawadd = '<MISSING>'
                    yield [website, name, rawadd, address, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
