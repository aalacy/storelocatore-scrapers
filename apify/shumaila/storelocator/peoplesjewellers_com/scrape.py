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
    name =[]
    cleanr = re.compile(r'<[^>]+>')
    name.append('none')
    url = 'https://www.peoplesjewellers.com/store-finder'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")   
    state_list = soup.findAll('div', {'class': 'accordion clearfix test-1'})
   # print("states = ",len(state_list))
    p = 0
    for states in state_list:
        divlist = states.findAll('div',{'class':'col-md-3'})
        for div in divlist:
            #print(div)
            det = re.sub(cleanr,'\n',str(div))
            #print(det)
            det = det.splitlines()
            #print(det)
            title = ''
            street = ''
            city = ''
            state = ''
            phone = ''
            
            for dt in det:
                if dt == '' or dt.find('Curbside') > -1 or dt == 'Open To Public' or (dt.find('2020') > -1 and dt.find('on ') > -1) :
                    pass
                else:
                    if title == '':
                        title = dt.lstrip()
                    elif street == '':
                        street = dt.lstrip().replace(' &amp;','&')
                    elif city == '':
                        #print(street,dt)
                        city,state = dt.lstrip().split(', ')
                    elif phone == '':
                        phone = dt.lstrip()
                    
                
           
            if title == 'Rideau Centre':
                street = '50 Rideau Street 262'
                city = 'Ottawa'
                state = 'ON'
                phone = '613-237-4587'
            else:                
                pass
            data.append(['https://www.peoplesjewellers.com/','https://www.peoplesjewellers.com/store-finder',title,street,city,state,'<MISSING>','CA','<MISSING>',phone,'<MISSING>','<MISSING>','<MISSING>','<MISSING>'])
            #print(p,data[p])
            p += 1
            
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
