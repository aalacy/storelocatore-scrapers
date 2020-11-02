from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('petrosbrand_com')



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
    url = 'https://www.petrosbrand.com/locations'
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    maindiv = soup.findAll('div',{'class':'field__item'})[2]
    maindiv = maindiv.findAll('a')
    for rep in maindiv:
        link ='https://www.petrosbrand.com' + rep['href']
        #logger.info(link)
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, 'html.parser')
        divlist = soup.findAll('div',{'class':'text-box'})
        flag = 0
        hours = ''
        street =''
        state =''
        pcode =''
        city = ''
        phone = ''
        for div in divlist:
            
            try:
                
                if div.text.find('Hours') > -1:
                    hours = div.text.replace('\n',' ').replace('Hours','').replace('pm',' pm').lstrip().rstrip()
                    #logger.info(hours)
                if div.text.find('Location') > -1:
                    det = div.text.split('Location')[1].lstrip().split('[')[0].splitlines()
                    street = det[0]
                    temp = []
                    temp = det[1].split(' ')
                    pcode = temp[-1]
                    state = temp[-2]
                    city = link.split('locations/petros-',1)[1].replace('-',' ')
                    phone = det[2]
                    #logger.info(det)
                    coord = div.find('a',{'class':'btn'})['href']
                    r = session.get(coord, headers=headers, verify=False)
                    coord = r.url
                    #logger.info(coord)
                    coord = coord.split('@',1)[1].split(',17z' ,1)[0]
                    lat,longt = coord.split(',')
                    title = soup.find('h1',{'class':"page-header"}).text
                    data.append([
                        'https://www.petrosbrand.com/',
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
                
                    
            except Exception as e:
                logger.info(e)
                pass

       

            
                
                
            
  
    
      

           
            
                
                
                
             
                
           
                

                
                
            
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
