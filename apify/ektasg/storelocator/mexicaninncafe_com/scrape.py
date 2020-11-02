from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mexicaninncafe_com')



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
    hourlist = []
    pattern = re.compile(r'\s\s+')
    p =0
    url = 'https://www.mexicaninncafe.com/locations-3'
    r = session.get(url, headers=headers, verify=False)
    soup =BeautifulSoup(r.text, "html.parser")
    maindiv = soup.find('section',{'class':'Main-content'})
    divlist = maindiv.findAll('div',{'class':'col sqs-col-12 span-12'})
    maplist = soup.findAll('div',{'class':'map-block'})
    logger.info(len(maplist))
    for i in range(0,1):
        mainlist = str(divlist[i])   
        start =0
        
        while True:
            start = mainlist.find('<h2 ',start)
            if start == -1:            
                break
            else:
                start = start + 3
            end = mainlist.find('View Menu',start)
            if end == -1:
                end = len(mainlist)-1
                
            det = mainlist[start-3:end]            
            hourlist.append(det)
            start = end + 3
            
 
    logger.info(len(hourlist))
    flag = 0
    for divn in maplist:        
        div = json.loads(divn['data-block-json'])        
        #title = div['location']['addressTitle'].replace('Mexican Inn Cafe ','').upper()
        street = div['location']['addressLine1']
        city,state= div['location']['addressLine2'].split(', ',1)
        try:
            state,pcode = state.lstrip().split(', ',1)
        except:
            state,pcode = state.lstrip().split(' ',1)
        
        lat = div['location']['mapLat']
        longt = div['location']['mapLng']
     
        hours = ''
        phone = '<MISSING>'
        title= '<MISSING>'
        for det in hourlist:
            det = BeautifulSoup(det,'html.parser')
            
            if det.find('p').text.find(pcode) > -1:
                if pcode == '76107':
                    flag = flag + 1
                #logger.info(pcode)
                title = det.find('h2').text
                if flag == 2:
                    title = 'HENDERSON STREET'
                    hours= 'Temporarily Closed'
                    phone = '(817) 336-2164'
                    flag = 1
                    break
                hourm = det.findAll('h3')                
                for hr in hourm:
                    hours = hours + hr.text + ' '
                    
                phone = det.find('a').text
                break            
        data.append([
                        'https://www.mexicaninncafe.com/',
                        'https://www.mexicaninncafe.com/locations-3',                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                         '<MISSING>',
                        phone,
                         '<MISSING>',
                        lat,
                        longt,
                        re.sub(pattern,' ',hours)
                    ])
        #logger.info(p,data[p])
        p += 1
   
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
