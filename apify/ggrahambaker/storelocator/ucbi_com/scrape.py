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
    url = 'https://www.ucbi.com/locations/'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.findAll('article')
    #print(len(divlist))
   
   # print("states = ",len(state_list))
    p = 0
    for div in divlist:       
        store = div['data-id']
        lat = div['data-lat']
        longt = div['data-lng']
        street = div['data-street']
        city = div['data-citystatezip']
        city,state = city.split(', ',1)
        state,pcode = state.lstrip().split(' ',1)
        title = div['aria-label']
        link = 'https://www.ucbi.com'+div.find('a')['href']
        ltype = div.find('div',{'class':'options'}).text
        if 'Branch' in ltype or 'Office' in ltype:
            ltype = ltype.lstrip().replace('\n','|')
        else:
            continue
        hours = div.find('div',{'class':'hours'}).text        
        r = session.get(link, headers=headers, verify=False)    
        soup =BeautifulSoup(r.text, "html.parser")
        try:
            phone = soup.find('p',{'itemprop':'telephone'}).text
            
        except:
            phone = '<MISSING>'
        try:
            hours = hours.split('Drive Up Hours',1)[0]
        except:
            pass
        hours = hours.replace('\n','').replace('Lobby Hours','')
        ltype = ltype.replace('Branch|','Branch')
        try:
            phone = phone.split(' (1-',1)[1].split(')',1)[0]
        except:
            pass
        data.append(['https://www.ucbi.com',link,title,
                        street,city,state,pcode.strip(),'US',
                        store,phone,ltype,lat,longt,hours
                    ])
        #print(p,data[p])
        p += 1
        
       
    return data


def scrape():
   
    data = fetch_data()
    write_output(data)

scrape()
