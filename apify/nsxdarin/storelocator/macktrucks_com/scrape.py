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
    url = 'https://www.macktrucks.com/simpleprox.ashx?http://mvservices.liquidint.com/DealerJSON_new.ashx'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    website = 'macktrucks.com'
    for line in r.iter_lines(decode_unicode=True):
        if '"IDENTIFIER_VALUE":"' in line:
            items = line.split(',"SELECT_EMAIL_ADDRESS":""},"')
            for item in items:
                if '"COMPANY_DBA_NAME":"' in item:
                    loc = '<MISSING>'
                    store = item.split('"')[0]
                    name = item.split('"COMPANY_DBA_NAME":"')[1].split('"')[0]
                    add = item.split(',"MAIN_ADDRESS_LINE_1_TXT":"')[1].split('"')[0]
                    city = item.split('"MAIN_CITY_NM":"')[1].split('"')[0]
                    state = item.split('"MAIN_STATE_PROV_CD":"')[1].split('"')[0]
                    country = item.split('"COUNTRY_CD":"')[1].split('"')[0]
                    add = add + ' ' + item.split(',"MAIN_ADDRESS_LINE_2_TXT":"')[1].split('"')[0]
                    add = add.strip()
                    lat = item.split('"MAIN_LATITUDE":"')[1].split('"')[0]
                    lng = item.split('"MAIN_LONGITUDE":"')[1].split('"')[0]
                    phone = item.split(',"REG_PHONE_NUMBER":"')[1].split('"')[0]
                    if phone == '':
                        phone = '<MISSING>'
                    hours = ''
                    zc = item.split(',"MAIN_POSTAL_CD":"')[1].split('"')[0]
                    typ = item.split('"DEALER_TYPE_DESC":"')[1].split('"')[0]
                    if ',"Sales":{' in item:
                        days = item.split(',"Sales":{')[1].split('}},')[0].split('"Start":"')
                        hours = 'Sun: ' + days[1].split('"')[0] + '-' + days[1].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Mon: ' + days[2].split('"')[0] + '-' + days[2].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Tue: ' + days[3].split('"')[0] + '-' + days[3].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Wed: ' + days[4].split('"')[0] + '-' + days[4].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Thu: ' + days[5].split('"')[0] + '-' + days[5].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Fri: ' + days[6].split('"')[0] + '-' + days[6].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Sat: ' + days[7].split('"')[0] + '-' + days[7].split('"End":"')[1].split('"')[0]
                        hours = hours.replace('Closed-Closed','Closed')
                    if '"Leasing":{' in item and hours == '':
                        days = item.split('"Leasing":{')[1].split('}},')[0].split('"Start":"')
                        hours = 'Sun: ' + days[1].split('"')[0] + '-' + days[1].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Mon: ' + days[2].split('"')[0] + '-' + days[2].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Tue: ' + days[3].split('"')[0] + '-' + days[3].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Wed: ' + days[4].split('"')[0] + '-' + days[4].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Thu: ' + days[5].split('"')[0] + '-' + days[5].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Fri: ' + days[6].split('"')[0] + '-' + days[6].split('"End":"')[1].split('"')[0]
                        hours = hours + '; Sat: ' + days[7].split('"')[0] + '-' + days[7].split('"End":"')[1].split('"')[0]
                        hours = hours.replace('Closed-Closed','Closed')
                    if country == '' or 'STATE' in country:
                        country = 'US'
                    if country == 'CANADA':
                        country = 'CA'
                    if country != 'MEXICO':
                        if hours == '':
                            hours = '<MISSING>'
                        if zc == '':
                            zc = '<MISSING>'
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
