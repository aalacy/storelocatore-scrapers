import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
           'authority': 'www.ihop.com',
           'method': 'POST',
           'path': '/api/sitecore/Locations/LocationSearchAsync',
           'scheme': 'https',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest',
           'adrum': 'isAjax:true',
           'cookie': '__cfduid=df5fcb2cc9d003943c8e68dc953e2d50a1572970879; ihop#lang=en; ASP.NET_SessionId=mfdizdb2tscz4vzxc550scnd; HamburgerTest=Control; menu-sort-test-1-2=default; CrossSellGuest=PreCheckout|1; __RequestVerificationToken=XmRgKVJm1Xl0QMfwWhmo8clGkv2_oGc3oO7M4taAWKo2V_TuROBpqYLGdqMY5ycLVn6m0SmiRJOX69H7tH4sKaBrEjZAdX0L8H6eb8UcibU1; _gcl_au=1.1.1950433582.1572970854; _ga=GA1.2.141535309.1572970854; _fbp=fb.1.1572970855978.757237160; _gid=GA1.2.989343254.1573232460; SC_ANALYTICS_GLOBAL_COOKIE=c3c5f60445914e1bb7ba1581eb74c9a2|True; ClientTime=11:03:13 AM; my-location=f1db6ad3-81c6-49d2-a772-ae8b34d8d6d8|40489|Richmond%20Hill%2C%20ON|||False|False|5437|True; ADRUM=s=1573232675208&r=https%3A%2F%2Fwww.ihop.com%2Fen%2Frestaurants%3F-1455927552; AWSALB=Dct3cOrNiNbL8MntIw/wI1O6Ex+w7ds+05mMj6HQx4bpaNrxGGkVxDL4K6LGUGuPQb/59UcBOWGtxAfI3gnRDKmFvuCIDk682348m+kc3HY74S+FkaBdlD5rCNeJ'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.ihop.com/api/sitecore/Locations/LocationSearchAsync'
    payload = {'ResultsPage': '/locations/results',
               'LocationRoot': '{B14FE50A-1FFB-40C5-AE70-999D66C2ECDB}',
               'NumberOfResults': '5000',
               'LoadResultsForCareers': 'False',
               'MaxDistance': '10000',
               'UserLatitude': '',
               'UserLongitude': '',
               'SearchQuery': '10002',
               '__RequestVerificationToken': 'IPW5pXDKbmqnfuVlNv3KEbNEn-S08AUd8V5fBrsJ1VK7-Zmy8Aowf003XyRrl8ccG4IMiN5CnjPD5YyUlfXyxfhrXByMHvhCvWh_Qtyp6H41'
               }
    locs = []
    r = session.post(url, headers=headers, data=payload)
    array = json.loads(r.content)
    Found = True
    for item in array['Locations']:
        store = item['Location']['StoreNumber']
        name = item['Location']['Name']
        add = item['Location']['Street']
        city = item['Location']['City']
        state = item['Location']['State']
        country = item['Location']['Country']
        zc = item['Location']['Zip']
        try:
            phone = item['Contact']['Phone']
        except:
            phone = '<MISSING>'
        lat = item['Location']['Coordinates']['Latitude']
        lng = item['Location']['Coordinates']['Longitude']
        website = 'ihop.com'
        typ = 'Restaurant'
        try:
            hours = 'Sun: ' + item['HoursOfOperation']['DaysOfOperation'][0]['OpenHours'] + '-' + item['HoursOfOperation']['DaysOfOperation'][0]['CloseHours']
            hours = hours + '; Mon: ' + item['HoursOfOperation']['DaysOfOperation'][1]['OpenHours'] + '-' + item['HoursOfOperation']['DaysOfOperation'][1]['CloseHours']
            hours = hours + '; Tue: ' + item['HoursOfOperation']['DaysOfOperation'][2]['OpenHours'] + '-' + item['HoursOfOperation']['DaysOfOperation'][2]['CloseHours']
            hours = hours + '; Wed: ' + item['HoursOfOperation']['DaysOfOperation'][3]['OpenHours'] + '-' + item['HoursOfOperation']['DaysOfOperation'][3]['CloseHours']
            hours = hours + '; Thu: ' + item['HoursOfOperation']['DaysOfOperation'][4]['OpenHours'] + '-' + item['HoursOfOperation']['DaysOfOperation'][4]['CloseHours']
            hours = hours + '; Fri: ' + item['HoursOfOperation']['DaysOfOperation'][5]['OpenHours'] + '-' + item['HoursOfOperation']['DaysOfOperation'][5]['CloseHours']
            hours = hours + '; Sat: ' + item['HoursOfOperation']['DaysOfOperation'][6]['OpenHours'] + '-' + item['HoursOfOperation']['DaysOfOperation'][6]['CloseHours']
        except:
            hours = '<MISSING>'
        if 'Sun: -' in hours:
            hours = '<MISSING>'
        if state == 'HI':
            Found = False
        if Found or state == 'HI':
            if zc != '':
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
