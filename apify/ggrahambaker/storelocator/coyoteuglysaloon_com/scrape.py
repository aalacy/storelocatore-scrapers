import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('coyoteuglysaloon_com')



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
    url = 'https://www.coyoteuglysaloon.com/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    state_list = soup.find('select', {'name': 'site'})
    state_list = state_list.findAll('option')
    #logger.info(len(state_list))
    flag = 0 
    for i in range(2,len(state_list)):
        link = state_list[i]
        #logger.info(link.text)
        if link.text.find('--') > -1 :
            break
        else:            
            link = link['value']
            r1 = session.get(link, headers=headers, verify=False)
            soup1 =BeautifulSoup(r1.text, "html.parser")
            maindiv = soup1.find('div',{'id':'mapinfo'})
            title = maindiv.find('dt').text

            address = maindiv.find('dd').text.splitlines()
            m = 0
            street = address[m]
            m += 1
            if address[m].find(',') == -1:
                street = street + ' '  + address[m]
                m += 1
            #logger.info(address[m])
            city,state = address[m].split(', ')
            state =state.lstrip()
            state,pcode = state.split(' ')
            maindiv = soup1.find('div',{'id':'detailinfo'})
            maindiv = maindiv.findAll('dd')
            phone = maindiv[0].text
            hourd = maindiv[2].findAll('li')
            hours = ''
            for hr in hourd:
                hours = hours + ' ' + hr.text

            if len(hours) < 2:
                hours = '<MISSING>'
            else:
                hours = hours.replace('am',' am').replace('pm',' pm').replace('-',' - ').replace('  ',' ')

            soup1 = str(soup1)
            start = soup1.find('"id"')
            if start == -1:
                store = '<MISSING>'
            else:
                start = soup1.find(':',start)
                start = soup1.find('"',start)+1
                end = soup1.find('"',start)
                store = soup1[start:end]
            start = soup1.find('"lat"')
            if start == -1:
                lat = '<MISSING>'
            else:
                start = soup1.find(':',start)
                start = soup1.find('"',start)+1
                end = soup1.find('"',start)
                lat = soup1[start:end]
            start = soup1.find('"lng"')
            if start == -1:
                longt = '<MISSING>'
            else:
                start = soup1.find(':',start)
                start = soup1.find('"',start)+1
                end = soup1.find('"',start)
                longt = soup1[start:end]

            if phone.find('UGLY') > -1 and phone.find('(') == -1:                
                phone = phone.replace('UGLY','8459')
                
            elif phone.find('UGLY') > -1 and phone.find('(') > -1:                
                phone = phone.replace('UGLY ','')
                
            data.append([
                        'https://www.coyoteuglysaloon.com/',
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
            #logger.info(p,data[p])
            p += 1
                
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
