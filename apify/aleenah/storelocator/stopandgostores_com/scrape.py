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
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.stopandgostores.com/locations'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")
    linklist = soup.select('a:contains("Store Profile")')
   # print("states = ",len(state_list))
    p = 0
    for link in linklist:
        
        link = link['href']       
        r = session.get(link, headers=headers, verify=False)    
        soup =BeautifulSoup(r.text, "html.parser")      
        title = soup.find('h6').text.strip()        
        content = soup.text.split('S&G #',1)[1].split('Phone',1)[0].lstrip()       
        content = filter(None, re.split("([A-Z][^A-Z]*)", content))
        content = ' '.join(content)
        content = content.replace('\n',' ').strip()        
        street,state = content.split(', ',1)
        #store,street = street.split(' ',1)
        content = state.replace(' ','').strip()
        state = content[0:2]
        pcode = content[2:7]
        if pcode.isdigit():
            pass
        else:
            if state.find('Mi') > -1:                
                state = content.split(' ',1)[0]
                content = content.split(' ',1)[1]

            else:
                content = content[2:]
                res = re.findall(r'(\w+?)(\d+)', content)[0]
                #print(res)
                state = state+res[0]
                content = content.replace(res[0],'')
               
            pcode = content[0:5]
           
        phone = content[7:]        
        city = street.split(' ')[-1]
        street = street.replace(city,'')
        store = title.split('#',1)[1].split('(')[0].strip()
        street= street.split(store,1)[1].strip()
        #title = 'S&G #'+str(store)

        if street == '':
            street = city
        street = street.replace('( In& Out)','')
        if phone.find('--') > -1 or 'X' in phone:
            phone = '<MISSING>'
        data.append([
                        'https://www.stopandgostores.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>'
                    ])
        #print(p,data[p])
        p += 1
                
            
            
       
        
    return data


def scrape():
    
    data = fetch_data()
    write_output(data)
  

scrape()
