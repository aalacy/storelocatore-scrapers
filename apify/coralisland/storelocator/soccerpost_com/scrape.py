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
    url = 'https://www.soccerpost.com'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split('SP.stores = ')[1].split('];')[0]
    r = r+']'
    
    print(r)
    loclist = r.replace('\n',' ').split('},')
    for loc in loclist:
        title = loc.split('name: "',1)[1].split('"',1)[0]
        store = '<MISSING>'
        lat = loc.split('latitude: ',1)[1].split(',',1)[0]
        longt = loc.split('longitude: ',1)[1].split(',',1)[0]
        street = loc.split('address: "',1)[1].split('"',1)[0]
        city = loc.split('city: "',1)[1].split('"',1)[0]
        state = loc.split('state: "',1)[1].split('"',1)[0]
        pcode = loc.split('zip: "',1)[1].split('"',1)[0]
        ccode = 'US'
        
        phone = loc.split('phone: "',1)[1].split('"',1)[0]
        try:
            longt = longt.split('}',1)[0]
        except:
            pass
        if street.find('coming soon!') == -1:
            data.append([
                'https://www.soccerpost.com',
                'https://www.soccerpost.com',                   
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
                '<MISSING>'
            ])
            #print(p,data[p])
            p += 1
        
  
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

