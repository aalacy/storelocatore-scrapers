from bs4 import BeautifulSoup
import csv
import string
import re, time, json

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bordergrill_com')



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

    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.bordergrill.com/locations/'
    r = session.get(url, headers=headers, verify=False)  
    
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.findAll('div', {'class': "col-md-6"})    
    p = 0
    for div in divlist:
        try:
            title = div.find('h2').text
            if title.find('Truck') > -1:
                continue            
            content = re.sub(cleanr,'\n',str(div))
            det = re.sub(pattern,'\n',str(content))
            content = det.lstrip().splitlines()
            street = content[1]
            city,state = content[2].split(', ',1)
            state,pcode = state.lstrip().split(' ',)
            phone = content[3]
            link = 'https://www.bordergrill.com' + div.find('a',{'class':'btn-brand'})['href']
            if phone.find('Direction') > -1:
                phone = '<MISSING>'
            #logger.info(link)
            try:
                hours = det.split('Hours')[1].split('\n',1)[1].split('View',1)[0]
                hours = hours.replace('\n', ' ')
                try:
                    hours = hours.split('(',1)[0]
                except:
                    pass
            except:
                hours = '<MISSING>'
            if hours == '<MISSING>':
                r = session.get(link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text,'html.parser')
                #logger.info('1')
                try:
                    hours = soup.text.split('Sun-Mon',1)[1].split('\n',1)[0].replace('pm','pm ').replace('Closed','Closed ')
                    hours = 'Sun-Mon'+hours
                except:
                    try:
                        hours = soup.text.split('Mon – Sun',1)[1].split('\n',1)[0].replace('pm','pm ').replace('Closed','Closed ')
                        hours = 'Mon – Sun'+hours
                    except:
                        hours = '<MISSING>'
           
            coord = div.find('a')['href']           
            if coord.find('@') == -1:
                r = session.get(coord, headers=headers, verify=False)
                coord = r.url
            lat,longt = coord.split('@',1)[1].split('data',1)[0].split(',',1)
            longt = longt.split(',',1)[0]
            
           
            data.append([
                            'https://www.bordergrill.com',
                            link,                   
                            title,
                            street.replace(',',''),
                            city,
                            state,
                            pcode,
                            'US',
                            '<MISSING>',
                            phone,
                            '<MISSING>',
                            lat,
                            longt,
                            hours.replace('•','')
                        ])
            #logger.info(p,data[p])
            p += 1
                    
                
            
        except:
            pass
        
           
        
    return data


def scrape():   
    data = fetch_data()
    write_output(data)
   
scrape()
