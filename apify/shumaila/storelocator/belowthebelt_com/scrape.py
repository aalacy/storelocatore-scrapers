import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time

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
    url = 'https://www.belowthebelt.com/pages/stores'
    r = session.get(url, headers=headers, verify=False)
    time.sleep(8)
    soup =BeautifulSoup(r.text, "html.parser")
   
    state_list = soup.findAll('div', {'class': 'store-box'})
   
    print(len(state_list))   
    for i in range(1,len(state_list)):
        det = state_list[i]
        #print(det)
        try:
            title = det.find('h3').text
            li = det.findAll('li')
           
            temp = li[1].text
            phone = li[2].text
            address = []
            address = temp.split(',')
            s = -1
            state = address[s].lstrip()
            end = len(address) - 3
            if len(state) > 3:
                s= s-1
                end = len(address) - 3
                state = address[s].lstrip()
            pcode = address[s-1].lstrip()
            city = address[s-2].lstrip()
            
            street = ''
            for k in range(0,end):
                street = street + ' ' + address[k].lstrip()
            if len(pcode.rstrip().lstrip()) > 8:
                street = street + ' ' + city.lstrip()
                city,pcode = pcode.lstrip().split(' ',1)
            #print(street)
            #input()
                
            
            data.append([
                        'https://www.belowthebelt.com/',
                        url,                   
                        title,
                        street.lstrip(),
                        city.lstrip(),
                        state.lstrip(),
                        pcode.lstrip(),
                        'CA',
                        '<MISSING>',
                        phone.replace('\n','').lstrip(),
                        '<MISSING>',
                       '<MISSING>',
                        '<MISSING>',
                        '<MISSING>'
                    ])
            #print(p,data[p])
            p += 1
        except:
            pass
                    
                
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
