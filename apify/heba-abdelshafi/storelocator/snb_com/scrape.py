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
    url = 'https://snb.com/locations?range=20'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text,'html.parser')
    divlist = soup.find('table',{'id':'locations'}).findAll('tr')
    loclist = r.text.split('locations=',1)[1].split('];',1)[0]
    loclist = json.loads(loclist+']')
    print(len(divlist))    
    for i in range(1,len(divlist)):
        div = divlist[i]
        address =div.findAll('td')[0].text.splitlines()
        #print(address)
        title = address[1]
        street = address[2].replace('\t','')
        try:
            city,state = address[3].replace('\t','').split(', ')
        except:
            street = street + ' ' + address[3]
            city,state = address[4].replace('\t','').split(', ')
            
        pcode = state.rstrip().split(' ')[-1]
        state = state.replace(' '+pcode,'')
        try:
            phone =div.findAll('td')[1].text.splitlines()[2]
        except:
            phone = '<MISSING>'
        try:
            hours = div.findAll('td')[2].text.replace('\n','')
        except:
            hours = '<MISSING>'
        try:
            hours = hours.split('Drive')[0]
        except:
            pass
        try:
            hours = hours.split('Trans')[0]
        except:
            pass
        det =div.findAll('td')[3].text
        ltype = 'Branch'
        if det.find('ATM Only') > -1:
            ltype = 'ATM'
        elif det.find('ATM') > -1:
            ltype = ltype + '| ATM'
        store = div['id'].replace('location','')
        lat = '<MISSING>'
        longt = '<MISSING>'
        for loc in loclist:
            if store == loc['id']:
                lat = loc['latitude']
                longt = loc['longitude']
                break
        if len(hours) < 3:
            hours = '<MISSING>'
        data.append([
                'https://snb.com/',
                'https://snb.com/locations',                   
                title,
                street,
                city,
                state,
                pcode,
                'US',
                store,
                phone,
                ltype,
                lat,
                longt,
                hours
            ])
        #print(p,data[p])
        p += 1
            
        
        
        #input()
   
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

