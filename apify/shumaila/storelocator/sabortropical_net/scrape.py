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
    pattern = re.compile(r'\s\s+') 
    url = 'https://sabortropical.net/locations/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.findAll('div', {'class': 'fl-col-content fl-node-content'})
    #print("states = ",len(divlist))
    for div in divlist:
        if div.find('div',{'class':'fl-html'}):
            det = re.sub(pattern,' ',div.text).splitlines()            
            title = det[0].lstrip()
            try:
                store = title.split('#')[1]
            except:
                store = '<MISSING>'
            try:
                street = det[1]
            except:
                continue
           
            city,state = det[2].split(', ')
            state,pcode = state.lstrip().split(' ',1)
            hours = det[3]+' '+det[4] + ' '+det[5]
            phone = det[6]
            coord = div.find('div',{'class':'fl-html'}).find('iframe')['src']
            longt,lat = coord.split('!2d',1)[1].split('!2m')[0].split('!3d')            
            phone = phone.replace('Phone:','').lstrip()
            if phone.find('(305) 266-667') > -1:
                phone = '(305) 266-6678'
            data.append([
                        'https://sabortropical.net/',
                        'https://sabortropical.net/locations/',                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
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
