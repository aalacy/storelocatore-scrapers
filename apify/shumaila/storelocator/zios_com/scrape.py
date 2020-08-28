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
    cleanr = re.compile(r'<[^>]+>')
    pattern = re.compile(r'\s\s+')
    p = 0
    url = 'https://zios.com/locations/?disp=all'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.findAll('div', {'class': 'loc-panel'})
    print("states = ",len(divlist))
    for div in divlist:
        det = div.findAll('li',{'class':'col-md-6'})
        for dt in det:
            txtnow = re.sub(cleanr,'\n',str(dt))
            txtnow = re.sub(pattern, '\n' ,txtnow).replace('[','').replace(']','').lstrip().splitlines()
            title = txtnow[0]
            street= txtnow[1]
            city,state = txtnow[2].split(', ')
            try:
                city = city.split(' (')[0]
            except:
                pass            
            state,pcode =state.lstrip().split(' ',1)
            try:
                temp,pcode = pcode.lstrip().rstrip().split(' ',1)
                state = state + ' '+temp
            except:
                pass
            phone = txtnow[3].replace('Phone:','').lstrip()
            hours = ''
            flag = 0
            for m in range(3,len(txtnow)):
                if txtnow[m].find('day')> -1 or txtnow[m].find('AM') > -1:
                    
                    hours = hours + txtnow[m] + ' '
                else:
                    pass
                           
                        
            print(txtnow)
            print(phone,hours)
            data.append([
                        'https://zios.com/',
                        'https://zios.com/locations/?disp=all',                   
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
            print(">>>>>>>>>>>>")
       
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
