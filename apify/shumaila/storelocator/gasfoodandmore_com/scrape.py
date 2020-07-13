from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://gasfoodandmore.com/wp-admin/admin-ajax.php?action=store_search&lat=44.523579&lng=-89.574563&max_results=25&search_radius=50&autoload=1'
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()
    cleanr = re.compile(r'<[^>]+>')
    #loclist = json.loads(r)
    for loc in loclist:
        title = loc['store'].replace('&#8211;','-')
        store = loc['store'].split('The Store ')[1].split('#')[1].split(' ')[0]
        lat = loc['lat']
        longt = loc['lng']
        street = loc['address'].split(',')[0]
        city = loc['city']
        state = loc['state']
        pcode = loc['zip']
        ccode = loc['country']
        hours = loc['hours']
        hours = re.sub(cleanr,' ',str(hours)).strip().replace('  ',' ')
        if ccode.find('United') > -1:
            ccode = 'US'
        phone = loc['phone']
        if state.find('Wisconsin') > -1:
            state = 'WI'
       
        data.append([
                'https://gasfoodandmore.com/',
                'https://gasfoodandmore.com/locations/',                   
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                '<MISSING>',
                lat,
                longt,
                hours
            ])
        print(p,data[p])
        p += 1
        
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

