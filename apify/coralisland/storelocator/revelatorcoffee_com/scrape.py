from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('revelatorcoffee_com')



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
    url = 'https://revelatorcoffee.com/pages/locations'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    linklist = soup.find('div',{'class':'grid'}).findAll('a')
    logger.info(len(linklist))  
    p = 0
    for link in linklist:
        
        link = link['href']
        #logger.info(link)
        r = session.get(link, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        try:
            content = soup.find('div',{'class':'rte grid__item'}).find('table').findAll('tr')            
            for dt in content:
                try:
                    lat,longt = dt.find('a')['href'].split('@',1)[1].split('data',1)[0].split(',',1)
                    longt = longt.split(',',1)[0]
                except:
                    lat = '<MISSING>'
                    longt = '<MISSING>'
                    
                det = re.sub(pattern,' ',dt.text).splitlines()               
                title = det[0]
                address = det[1]
                hours = det[2]
                if hours.find('location is closed') > -1:
                    hours = 'Temporarily Closed'
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
                phone = '<MISSING>'
                data.append([
                        'https://revelatorcoffee.com/',
                        link,                   
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
                        hours
                    ])
                #logger.info(p,data[p])
                p += 1
                
            
            
            
        except:
            try:
                content = soup.find('div',{'class':'Footer-business-info'}).text.lstrip().splitlines()                
                title  = content[0]
                street = content[1]
                city, state,pcode = content[2].split(', ',2)               
                phone = content[4]
                #logger.info(phone)
                hours = soup.findAll('h1')[1].text.replace('WINE','').replace('PICKUP & DELIVERY','').lstrip().replace('ay','ay ').replace('-','- ')
                try:
                    lat = str(soup).split('"mapLat":',1)[1].split(',',1)[0]
                    longt = str(soup).split('"mapLng":',1)[1].split(',',1)[0]
                except:
                    lat = '<MISSING>'
                    longt = '<MISSING>'
                data.append([
                        'https://revelatorcoffee.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode.replace(',',''),
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        hours
                    ])
                #logger.info(p,data[p])
                p += 1
                    
                    
            except:
                continue
     
        
                  
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
