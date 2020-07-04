import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
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
    
    url = 'https://dougashy.com/locations/'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll('div',{'class':'fl-rich-text'})    
    print(len(divlist))  
    det = r.text.split('var wpgmaps_localize_marker_data = ')[1].split('var wpgmaps_localize_global_settings =')[0]
    det = re.sub(r'"[1-9]":', "", det)
    det = '['+det.replace(';',']').replace('}]',']')
    det = det.replace('[{','[')   
    coordlist = json.loads(det)  
    p = 0
    for div in divlist:
        if div.text.find('Address') > -1:
            title = div.find('h4').text
            det = div.findAll('p')
            address = det[0].text.splitlines()
            street = address[1]
            city,state = address[2].split(', ')
            state = state.lstrip()
            state,pcode = state.split(' ')
            phone = det[1].find('a').text
            hours = det[2].text.replace('\n', ' ').replace('Store Hours','').lstrip()
            lat = '<MISSING>'
            longt = '<MISSING>'
            for coord in coordlist:                
                if coord['address'].replace(',','').replace('.','').find(street.replace(',','').replace('.','')) > -1:
                    lat = coord['lat']
                    longt = coord['lng']
            data.append([
                        'https://dougashy.com/',
                        'https://dougashy.com/locations/',                   
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
            #input()
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
