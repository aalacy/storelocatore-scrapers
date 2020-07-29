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
    p = 0
    cleanr = re.compile(r'<[^>]+>')
    pattern = re.compile(r'\s\s+') 
    url = 'https://marksfeedstore.com/locations'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    store_list = soup.findAll('div', {'class': 'image-caption'})
    print(len(store_list))
    for store in store_list:
        text = re.sub(cleanr,'\n',str(store).lstrip())
        text = re.sub(pattern,'\n',text).splitlines()
        print(text)
        #input()
        title = text[1]
        street = text[2]
        city,state = text[3].split(', ')
        state,pcode = state.lstrip().split(' ',1)
        phone = text[4]
        hours = text[5]
        data.append(['https://marksfeedstore.com/','https://marksfeedstore.com/locations',title,street,city,state,pcode,'US',
                        '<MISSING>',phone,'<MISSING>','<MISSING>','<MISSING>',hours])
        #print(p,data[p])
        p += 1

        
    return data

def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
