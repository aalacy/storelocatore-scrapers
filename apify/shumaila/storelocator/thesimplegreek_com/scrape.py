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
    


    url = 'https://thesimplegreek.com/locations/'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('div',{'class':'flex_column'})
    print("states = ",len(divlist))
    p = 0
    pattern = re.compile(r'\s\s+')

    for div in divlist:
        try:
            div = div.text
            #print(div)
            #print(len(div))
            #input()
            while True: 
                if len(div) < 2:
                    break
                det = div.splitlines()
                #print(det)
                #print(len(det))
                #print(det)
                i = 0
                while True:
                    if det[i] == '':
                        i = i + 1
                    else:
                        title =det[i].replace('\xa0','')
                        break
                if title.find('Coming Soon') > -1:
                    break
                else:
                    i = i+1
                    street = det[i]
                    i = i + 1
                    while True:
                        try:
                            city,state = det[i].split(', ')
                            
                            state,pcode = state.lstrip().split(' ',1)
                            i = i+ 1
                            break
                            
                        except:
                            street = street + ' '+ det[i]

                        i = i+1
                            
                    phone = det[i].replace('\xa0','').replace('(GYRO)','').replace('Phone: ','').replace('GYRO ','')
                    try:
                        hours = det[i+1].replace('Hours:','').lstrip()
                        try:
                            hours = hours.split('Order',1)[0]
                        except:
                            pass
                    except:
                        hours = '<MISSING>'

                #print(p,title,street,city)
                data.append([
                        'https://thesimplegreek.com/',
                        'https://thesimplegreek.com/locations/',                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        hours
                    ])
                #print(p,data[p])
                p += 1
                
                #input()
                if len(det) < 13:
                    
                    break
                else:
                    try:
                        div = div.split('Directions',1)[1].lstrip()
                        div = re.sub(pattern,' ',div)
                    except:
                        break
                    
                    
               
            
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        except Exception as e:
            print(e)
            #input()
            pass
                
                    
     
            
            
        
        
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
