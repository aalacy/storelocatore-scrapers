import time
import csv
import urllib2
import requests
import json
import gzip

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'accept-encoding': 'gzip, deflate, br'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.kfc.co.uk/cms/api/data/restaurants_all'
    Found = True
    rc = 0
    while Found:
        try:
            rc = rc + 1
            time.sleep(1)
            print('Try %s...' % str(rc))
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                if '"id":' in r.content:
                    items = r.content.split('"id":')
                    for item in items:
                        if '"sfid":"' in item:
                            name = item.split('"name":"')[1].split('"')[0].encode('utf-8')
                            Found = False
                            website = 'kfc.co.uk'
                            typ = '<MISSING>'
                            store = item.split(',')[0]
                            hours = ''
                            country = 'GB'
                            add = item.split(',"shippingstreet":"')[1].split('"')[0].encode('utf-8')
                            city = item.split('"shippingcity":"')[1].split('"')[0].encode('utf-8')
                            state = '<MISSING>'
                            zc = item.split('"shippingpostalcode":"')[1].split('"')[0]
                            lat = item.split('"latitude":')[1].split(',')[0]
                            lng = item.split('"longitude":')[1].split(',')[0]
                            hours = 'Sun: ' + item.split('"kfc_sundayopening__c":"')[1].split('"')[0] + '-' + item.split('"kfc_sundayclosing__c":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Mon: ' + item.split('"kfc_mondayopening__c":"')[1].split('"')[0] + '-' + item.split('"kfc_mondayclosing__c":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Tue: ' + item.split('"kfc_tuesdayopening__c":"')[1].split('"')[0] + '-' + item.split('"kfc_tuesdayclosing__c":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Wed: ' + item.split('"kfc_wednesdayopening__c":"')[1].split('"')[0] + '-' + item.split('"kfc_wednesdayclosing__c":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Thu: ' + item.split('"kfc_thursdayopening__c":"')[1].split('"')[0] + '-' + item.split('"kfc_thursdayclosing__c":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Fri: ' + item.split('"kfc_fridayopening__c":"')[1].split('"')[0] + '-' + item.split('"kfc_fridayclosing__c":"')[1].split('"')[0]
                            hours = hours + '; ' + 'Sat: ' + item.split('"kfc_satdayopening__c":"')[1].split('"')[0] + '-' + item.split('"kfc_satdayclosing__c":"')[1].split('"')[0]
                            if hours == '':
                                hours = '<MISSING>'
                            loc = 'https://www.kfc.co.uk' + item['link'].replace('\\','')
                            if loc == 'https://www.kfc.co.uk':
                                loc = '<MISSING>'
                            phone = '<MISSING>'
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        except:
            Found = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
