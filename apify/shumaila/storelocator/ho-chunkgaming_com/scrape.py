from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ho-chunkgaming_com')



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
    
    url = 'https://ho-chunkgaming.com/'
    p = 0
    r= session.get(url, headers=headers, verify=False)
    soup =  BeautifulSoup(r.text,'html.parser')
    mainul = soup.find('nav',{'id':'menu'})
    linklist = mainul.findAll('a')
    for link in linklist:
        link = link['href']
        #logger.info(link)
        r= session.get(link, headers=headers, verify=False)
        soup =  BeautifulSoup(r.text,'html.parser')
        maindiv = soup.find('div',{'class':'footer-addr'}).text
        maindiv = re.sub(pattern,'\n',maindiv).lstrip().splitlines()
        #logger.info(maindiv)
        title = maindiv[0]
        street = maindiv[1]
        city ,state= maindiv[2].split(', ')
        state,pcode = state.lstrip().split(' ',1)
        phone = maindiv[3]
        hours = ''
        try:
            hours = soup.find('div',{'class':'container-answer'}).text
            if hours != '':
                hours = re.sub(pattern,' ',hours)
                try:
                    hours = hours.split(':')[1].lstrip()
                except:
                    try:
                        hours = hours.split('open')[1].lstrip()
                    except:
                        if hours.find('Unfortunately') > -1 or hours.find('has made changes to the program') > -1:
                            hours = '<MISSING>'
            else:
                hours =  '<MISSING>'
            
        except:
            pass
        if len(hours) < 2 or hours.find('ing yet. ') > -1 :
            hours =  '<MISSING>'
        else:
            hours = hours.replace('â\x80\x93','-').replace('\n','')
        #logger.info(hours)
        data.append([
                'https://www.ho-chunkgaming.com/',
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
                '<MISSING>',
                '<MISSING>',
                hours
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

