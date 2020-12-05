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
    p = 0    
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.ranchone.com/locator/'    
    r = session.get(url, headers=headers, verify=False)
    soup =BeautifulSoup(r.text, "html.parser")    
    divlist = str(soup.findAll('script',{'type':"text/javascript"})[1]).split('= {')    
    for div in divlist:       
        try:           
            content = '{'+str(div).split('}',1)[0]+'}'
            content = json.loads(content.replace("'",'"'))           
            store = str(content['StoreId'])
            lat = str(content['Latitude'])
            longt = str(content['Longitude'])
            street = content['Address']
            city = content['City']
            state = content['State']
            pcode = content['Zip']
            phone = content['Phone']
            title = 'Ranch One Store #'+store
            if len(phone) < 3:
                phone = '<MISSING>'
            link = 'https://www.ranchone.com/stores/'+str(store)            
            r = session.get(link, headers=headers, verify=False)
            soup =BeautifulSoup(r.text, "html.parser")
            hours = soup.text.split('Store Hours',1)[1].split('About',1)[0].replace('PM',' PM ').replace('AM',' AM').strip()
            data.append([
                        'https://www.ranchone.com/',
                        link,                   
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
            
            
        except:
            pass
      
         
    return data


def scrape():
    data = fetch_data()
    write_output(data)
 

scrape()
