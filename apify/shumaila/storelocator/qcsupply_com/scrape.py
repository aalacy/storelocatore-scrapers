from bs4 import BeautifulSoup
import csv
import string
import re, time, json

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
    p = 0
    url = 'https://www.qcsupply.com/locations/'
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split('{"items":',1)[1].split('}],"',1)[0]
    loclist = loclist +'}]'
    loclist = json.loads(loclist)
    for loc in loclist:
        store = loc['id']
        title = loc['name']
        ccode = loc['country']
        city = loc['city']
        pcode = loc['zip']
        street = loc['address']
        lat = loc['lat']
        longt = loc['lng']
        phone = loc['phone']        
        try:
            state = title.split(', ')[1]
        except:
            state = loc['state']

        hourlist = str(loc['schedule_string'])
        hourlist = json.loads(hourlist)        
        hours = ''
        link = 'https://www.qcsupply.com'+loc['website'].split('-',1)[0]+'/'+loc['website'].split('-',1)[1]
        link = link.replace('\\','')
        #print(link)
        for hr in hourlist:
            day = hr
            hr = hourlist[hr]
            #print(hr)            
            temp = (int)(hr['to']['hours'])
            if temp > 12:
                temp = temp-12
            if temp == 0:
                temp = 12
            starttemp = (int)(hr['from']['hours'])
            
                
            start = str(starttemp) +' : '+hr['from']['minutes']+ ' AM - '
            end = str(temp)+' : '+hr['to']['minutes']+ ' PM '
            hours = hours +day + ' '+start + end

            if starttemp == 0:
                hours = hours +day + ' Closed'
            

            
        try:
            phone = phone.split('/')[0]
        except:
            pass
        data.append([
                'https://www.qcsupply.com/',
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
