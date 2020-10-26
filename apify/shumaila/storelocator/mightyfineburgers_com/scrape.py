
#https://stockist.co/api/v1/u5383/locations/all.js?callback=_stockistAllStoresCallback

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
    url = 'https://mightyfineburgers.com/locations/'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    time.sleep(3)
    coordlist = r.text.split('var wpgmaps_localize_marker_data =')[1].split('var wpgmaps_localize_global_settings =')[0] 
    coordlist = '[' + re.sub(r'"[1-9]":','',coordlist).replace('};',']')
    coordlist = coordlist.replace('[ {','[')
    #print(coordlist)
    coordlist = json.loads(coordlist)
    soup = BeautifulSoup(r.text, 'html.parser')  
    loclist = soup.findAll('div',{'class':'accordion-container'})
    titlelist = soup.findAll('h4')
    hourd = soup.findAll('p')
    hourlist = []
    for hour in hourd:
        if hour.text.find('am') > -1 and hour.text.find('pm') > -1:
            hourlist.append(hour)
    #print(hourlist)
    for i in range(0,len(loclist)):        
        loc =loclist[i]
        title = titlelist[i].text
        loc  = re.sub(cleanr,' ',str(loc)).splitlines()
        #print(loc)
        m = 0
        street = loc[m].lstrip()
        m += 1
        state = ''
        while True:
            try:
                city, state = loc[m].split(', ',1)
                break
            except:
                street = street + ' '+ loc[m].lstrip()
                m += 1
            

        state = state.lstrip()       
        state,pcode= state.split(' ',1)
        m += 1
        try:
            phone =loc[m].rstrip()
        except:
            phone = '<MISSING>'
            
        hours = re.sub(cleanr,' ',str(hourlist[i])).replace('\n','')   
        for coord in coordlist:
            #print(coord['address'].lstrip().split(' ')[0])
            if street.find(coord['address'].lstrip().split(' ')[0]) > -1:
                lat = coord['lat']
                longt = coord['lng']               
        
        data.append([
                'https://mightyfineburgers.com/',
                'https://mightyfineburgers.com/locations/',                   
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

