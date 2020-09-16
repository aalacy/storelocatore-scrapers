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
    url = 'https://www.industriousoffice.com/locations'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    state_list = soup.findAll('a', {'class': 'btn-location'})
   # print("states = ",len(state_list))
    p = 0
    cleanr = re.compile(r'<[^>]+>')
    for states in state_list:        
        states = states['href']        
        r = session.get(states, headers=headers, verify=False)
        if r.text.find('Coming Soon') > -1:
            continue
        try:
            r = r.text.split('var marketLocations = ',1)[1].split('];',1)[0]
            loclist = json.loads(r+']')
            for loc in loclist:
                city = loc['city']
                state = loc['abbr']
                pcode = loc['zip']
                phone = loc['phone']
                street = loc['address']
                title = loc['locationTitle']
                lat = loc['latitude']
                longt = loc['longitude']            
                ccode = 'US'        
                link = loc['permalink'].replace('\\','')
                if state == 'Wisconsin':
                    state = 'WI'
                if phone != '':
                    data.append([
                            'https://www.industriousoffice.com/',
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
                            '<MISSING>'
                                    ])
                    #print(p,data[p])
                    p += 1
                    
        except:
            r = r.text.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0]
            r = json.loads(r)
            link = states
            title = r['name']
            phone = r['telephone']
            street = r['address']['streetAddress']
            city = r['address']['addressLocality']
            state = r['address']['addressRegion']
            pcode = r['address']['postalCode']
            lat = r['geo']['latitude']
            longt = r['geo']['longitude']
            if state == 'Wisconsin':
                    state = 'WI'
            if phone != '':
                data.append([
                            'https://www.industriousoffice.com/',
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
