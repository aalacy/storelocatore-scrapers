from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('storagepro_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
         
           'Accept': 'application/json, text/plain, */*'
          
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
    url = 'https://www.storagepro.com/'
    r = session.get(url, headers=headers, verify=False)
    statelist =[]
    streets = []
    soup =BeautifulSoup(r.text, "html.parser")
    #slist = r.text.split('state_slug:"')
    #for s in slist:
    #    if s.find('<!doctype html>')> -1:
    #        continue
    #    state ='https://www.storagepro.com/storage-units/'+ s.split('"',1)[0]+'/'
    #    statelist.append(state)
    #    #logger.info(state)'''
    divlist = soup.select("a[href*=storage-units]")
    for div in divlist:
        divlink = 'https://www.storagepro.com' + div['href']
        statelist.append(divlink)
        
    
    #logger.info(len(divlist))
    for div in statelist:
        divlink = div #'https://www.storagepro.com' + div['href']
        #logger.info(divlink)
        #continue
        r = session.get(divlink, headers=headers, verify=False)
        time.sleep(2)
        soup = BeautifulSoup(r.text,'html.parser')
        linklist = soup.findAll('a',{'class':'location-link'})
        #logger.info(len(linklist))
        #input()
        flag = 0
        if len(linklist) == 0:
            linklist.append(div)
            flag =1
            
        for link in linklist:

          
            if flag == 0:                
           
                link =  'https://www.storagepro.com' + link['href']
                r = session.get(link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text,'html.parser')
                link = r.url
            
            logger.info(link)
            det = soup.find('div',{'class':'facility-card'})
            title = det.find('h2').text
            address = det.find('div',{'class':'facility-address'}).text.replace('\n',' ').strip().replace('Located off','')
            try:
                phone = det.find('a',{'class':'phone'}).text.replace('\n','').strip()
            except:
                phone = '<MISSING>'
            try:
                hours = det.find('div',{'class':'office-hours'}).text
            except:
                hours = '<MISSING>'
            try:
                lat,longt = soup.find('div',{'class':'google-map'}).find('img')['src'].split('center=',1)[1].split('&',1)[0].split(',')
            except:
                lat = longt = '<MISSING>'
            address = usaddress.parse(address)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find('Occupancy') != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1

            street = street.lstrip().replace(',','')
            city = city.lstrip().replace(',','')
            state = state.lstrip().replace(',','')
            pcode = pcode.lstrip().replace(',','')
            if len(pcode) > 5:
                ccode = "CA"
            else:
                ccode= 'US'
            if len(hours) < 3:
                hours = '<MISSING>'
            if street in streets:
                continue
            streets.append(street)
            data.append([
                        'https://www.storagepro.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        ccode,
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        hours.replace('AM',' AM ').replace('PM',' PM ').replace('Closed','Closed ')
                    ])
            #logger.info(p,data[p])
            p += 1
                    
    
    return data


def scrape():  
    data = fetch_data()
    write_output(data)
   

scrape()
