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
    infos = []
    locs = []
    urls = ['https://spatial.virtualearth.net/REST/v1/data/1652026ff3b247cd9d1f4cc12b9a080b/FordEuropeDealers_Transition/Dealer?spatialFilter=nearby(53.4807593,-2.2426305,160.934)&$select=*,__Distance&$filter=CountryCode%20Eq%20%27GBR%27&$top=250&$format=json&key=Al1EdZ_aW5T6XNlr-BJxCw1l4KaA0tmXFI_eTl1RITyYptWUS0qit_MprtcG7w2F&Jsonp=collectResults&$skip=0','https://spatial.virtualearth.net/REST/v1/data/1652026ff3b247cd9d1f4cc12b9a080b/FordEuropeDealers_Transition/Dealer?spatialFilter=nearby(53.4807593,-2.2426305,160.934)&$select=*,__Distance&$filter=CountryCode%20Eq%20%27GBR%27&$top=250&$format=json&key=Al1EdZ_aW5T6XNlr-BJxCw1l4KaA0tmXFI_eTl1RITyYptWUS0qit_MprtcG7w2F&Jsonp=collectResults&$skip=250']
    for url in urls:
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"DealerID":"' in line:
                items = line.split(',"EntityID":"')
                for item in items:
                    if '"DealerID":"' in item:
                        website = 'ford.co.uk'
                        typ = item.split('"Brand":"')[1].split('"')[0]
                        lat = item.split('"Latitude":')[1].split(',')[0]
                        lng = item.split('"Longitude":')[1].split(',')[0]
                        name = item.split('"DealerName":"')[1].split('"')[0]
                        add = item.split('"AddressLine1":"')[1].split('"')[0] + ' ' + item.split('"')[0]
                        add = add.strip()
                        city = item.split('"Locality":"')[1].split('"')[0]
                        country = 'GB'
                        loc = 'https://www.ford.co.uk/dealer-locator#/dealer/' + item.split('"')[0]  
                        state = '<MISSING>'
                        zc = item.split('"PostCode":"')[1].split('"')[0]
                        store = item.split('"DealerID":"')[1].split('"')[0]
                        phone = item.split('"PrimaryPhone":"')[1].split('"')[0]
                        hours = '<MISSING>'
                        if phone == '':
                            phone = '<MISSING>'
                        if city == '':
                            city = '<MISSING>'
                        if add == '':
                            add = '<MISSING>'
                        if zc == '':
                            zc = '<MISSING>'
                        if '"ServiceMondayOpenTime":""' not in item:
                            hours = 'Mon: ' + item.split('"ServiceMondayOpenTime":"')[1].split('"')[0] + '-' + item.split('"ServiceMondayCloseTime":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Tue: ' + item.split('"ServiceTuesdayOpenTime":"')[1].split('"')[0] + '-' + item.split('"ServiceTuesdayOpenTime":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Wed: ' + item.split('"ServiceWednesdayOpenTime":"')[1].split('"')[0] + '-' + item.split('"ServiceWednesdayOpenTime":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Thu: ' + item.split('"ServiceThursdayOpenTime":"')[1].split('"')[0] + '-' + item.split('"ServiceThursdayOpenTime":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Fri: ' + item.split('"ServiceFridayOpenTime":"')[1].split('"')[0] + '-' + item.split('"ServiceFridayOpenTime":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Sat: ' + item.split('"ServiceSaturdayOpenTime":"')[1].split('"')[0] + '-' + item.split('"ServiceSaturdayOpenTime":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Sun: ' + item.split('"ServiceSundayOpenTime":"')[1].split('"')[0] + '-' + item.split('"ServiceSundayOpenTime":"')[1].split('"')[0]
                        addinfo = name + '|' + add + '|' + zc
                        if addinfo not in infos:
                            infos.append(addinfo)
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
