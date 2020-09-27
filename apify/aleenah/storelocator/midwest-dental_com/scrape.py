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
    data = []
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://midwest-dental.com/find-by-zip/'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split(' var locs = ')[1].split('}];')[0]+'}]'
    loclist = json.loads(r)
    #print(loclist)
    #input()
    for loc in loclist:
        title = loc['name']        
        lat = loc['lat']
        longt = loc['lng']
        street = loc['address']
        city = loc['city']
        state = loc['state']
        pcode = loc['zip']   
        phone = loc['phone']
        link = loc['url']
        try:
            if link.find('https://midwest-dental.com/locations') == -1:
                continue
        except:
            continue
        r = session.get(link, headers=headers, verify=False)
        try:
            soup = BeautifulSoup(r.text,'html.parser')
            hours = soup.text.split('Hours',1)[1].lstrip().split('\n',1)[1].split('*',1)[0].replace('\n',' ')
        except:
            hours = '<MISSING>'
        try:
            hours = hours.split('(',1)[0]
        except:
            pass
        data.append([
                'https://midwest-dental.com/',
                link,                   
                title,
                street,
                city,
                state,
                pcode,
                'US',
                '<MISSING>',
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

