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
        #print(states)
        r = session.get(states, headers=headers, verify=False)
        ccode = 'US'
        soup = BeautifulSoup(r.text, "html.parser")       
        city_list = soup.findAll('div', {'class': 'location-marker-til'})
        linklist = []
        for cities in city_list:
            cities = cities.findAll('div')[1]
            cities = cities.find('a',{'class':'gtm-view-details'})           
            link = cities['href']
            linklist.append(link)       
        if len(linklist) == 0:
            linklist.append(states)
        
        for link in linklist:
            #print(p,link)
            r = session.get(link, headers=headers, verify=False)            
            soup = BeautifulSoup(r.text, "html.parser")            
            if soup.text.lower().find('coming soon') == -1 and soup.text.lower().find('opening ') == -1 :
                maindiv = soup.find('address')
                coord = maindiv.find('a')['href']
                try:
                    phone = soup.find('a',{'class':'phone'}).text
                except:
                    phone = '<MISSING>'
                maindiv = re.sub(cleanr,' ',str(maindiv)).strip().splitlines()
                title = maindiv[0].lstrip()
                street = maindiv[1].lstrip()
                city,state = maindiv[2].lstrip().split(', ',1)
                state,pcode = state.lstrip().split(' ',1)
                try:
                    lat,longt = coord.split('@')[1].split(',',1)
                    longt = longt.split(',',1)[0]
                except:
                    try:
                        lat,longt = str(soup).split('"latitude":',1)[1].split(',',1)
                        longt = longt.split(':',1)[1].split('}',1)[0]
                    except Exception as e:
                        print(e)
                        lat = '<MISSING>'
                        longt = '<MISSING>'
                if len(state) > 2 and len(pcode) > 6:
                    pcode = pcode.split(',')[1]
                    state,pcode= pcode.lstrip().split(' ')
                    
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
            
    print(p)  
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
