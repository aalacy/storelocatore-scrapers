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
   
    data = []    
    url = 'https://www.famoussamsarizona.com/locations'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    store_list = soup.findAll('div', {'class': 'txtNew'})[2:]
    print(len(store_list))
    hours = ''
    t = 0
    for store in store_list:
        if store.text.find('BUSINESS HOURS') > -1:
            hours = store.text.split('BUSINESS HOURS')[1].replace('\n',' ').lstrip().split('LIKE US ON FACEBOOK')[0].replace('\u200b','')
            break
        t += 1      
      
    for p in range(0,t):        
        text = store_list[p].text.splitlines()
        title = text[0]
        street = text[1]
        city,state = text[2].split(', ')
        state,pcode = state.lstrip().split(' ',1)
        phone = text[3]
        data.append(['https://www.famoussamsarizona.com/','https://www.famoussamsarizona.com/locations',title,street,city,state,pcode,'US',
                        '<MISSING>',phone,'<MISSING>','<INACCESSIBLE>','<INACCESSIBLE>',hours])
        #print(p,data[p])               

        
    return data

def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
