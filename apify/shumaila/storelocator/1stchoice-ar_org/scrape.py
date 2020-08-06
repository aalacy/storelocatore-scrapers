
import requests
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
    url = 'https://1stchoice-ar.org/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=508634301d&load_all=1&layout=1'
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()
   
    for loc in loclist:
        title = loc['title']
        store = loc['id']        
        street = loc['street']
        city = loc['city']
        state = loc['state']
        pcode = loc['postal_code']
        ccode = loc['country']
        lat = loc['lat']
        longt = loc['lng']
        if ccode.find('Canada') > -1:
            ccode = 'CA'
        elif ccode.find('United') > -1:
            ccode = 'US'
        phone = loc['phone']
        link = loc['website'].replace('\\','')
        hourstr = loc['days_str'].split(',')
        hours = ''
        for i in range(0,len(hourstr)):
            start = loc['start_time_'+str(i+1)]
            end = loc['end_time_'+str(i+1)]
            hours = hours + hourstr[i] +' ' + start +' : ' + end +' '

        if link.find('http') == -1:
            link = 'http://www.1stchoice-ar.org' + link
        
        if title.find('Coming Soon') == -1:
            data.append([
                'https://1stchoice-ar.org/',
                link,                   
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
            #print(p,data[p])
            p += 1
        


    
                
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

