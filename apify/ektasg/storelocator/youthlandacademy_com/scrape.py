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
    url = 'https://www.youthlandacademy.com/location'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split('MapifyPro.Google(center')[1].split(', zoom,')[1]
    r = r.split(', map_instance,')[0]    
    loclist = json.loads(r)
    for loc in loclist:
        title = loc['post_title']
        link = 'https://www.youthlandacademy.com/locations/'+title.lower().replace(' ','-')+'?location='+title
        #print(link)
        #input()
        lat = loc['google_coords'][0]
        longt = loc['google_coords'][1]
        det = BeautifulSoup(loc['tooltip_content'],'html.parser')
        det = det.text.splitlines()
        street = det[0]
        city,state = det[1].split(', ',1)
        state = state.lstrip()
        state,pcode = state.split(' ',1)
        try:
            pcode = pcode.split(', ',1)[0]
        except:
            pass
        ccode = 'US'
        phone = det[2]
        hours = det[4].replace('am',' am ').replace('pm',' pm ')
        if phone.find('Opening soon!') == -1:
            data.append([
                    'https://www.youthlandacademy.com/',
                    link,                   
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    ccode,
                    '<MISSING>',
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

