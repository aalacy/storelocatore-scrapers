from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('extraspace_com')



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
    state_list = []
    pattern = re.compile(r'\s\s+')
    url = 'https://www.extraspace.com/help/accessibility-commitment/'
    try:
        r = session.get(url)#requests.get(url,timeout = 30)
        #time.sleep(8)
    except:
        pass
    #logger.info(r.text)
    
    soup =BeautifulSoup(r.text, "html.parser")
    #maindiv = soup.find('div',{'id':'self-storage-locations'})
    #logger.info(maindiv)
    maindiv = soup.findAll('a')
    for lt in maindiv:
        try:
            if lt['href'].find('SiteMap-') > -1:
                state_list.append("https://www.extraspace.com" + lt['href'])
        except:
            pass
        
    logger.info('sitemap',len(state_list))
    p = 0
    for alink in state_list:
       
        statelink = alink #"https://www.extraspace.com" + alink['href']
        #logger.info(statelink)
        try:
            r1 = session.get(statelink, headers=headers, verify=False)#requests.get(statelink,timeout = 30)
        except:
            pass
  
        soup1 =BeautifulSoup(r1.text, "html.parser")
        maindiv1 = soup1.find('div',{'id':'acc-main'})
        #logger.info(maindiv1)
        link_list = maindiv1.findAll('a')
        #logger.info("NEXT PAGE",len(link_list))
        for alink in link_list:
            if alink.text.find('Extra Space Storage #') > -1:
                link = "https://www.extraspace.com" + alink['href']
                #logger.info(link)
                #input()
                
                r2 = session.get(link, headers=headers, verify=False)#requests.get(link)
                
  
                soup2 =BeautifulSoup(r2.text, "html.parser")
                title = soup2.find('span',{'id': 'FacilityTitle'}).text
                street = soup2.find('span', {'id': 'ctl00_mContent_lbAddress'}).text
                city = soup2.find('span', {'id': 'ctl00_mContent_lbCity'}).text
                state = soup2.find('span', {'id': 'ctl00_mContent_lbState'}).text
                pcode = soup2.find('span', {'id': 'ctl00_mContent_lbPostalCode'}).text
                phone =soup2.find('span', {'class': 'tel'}).text
                detail = soup2.findAll('div',{'class': 'fac-info'})
                hdet = detail[2].text
                hdet = re.sub(pattern," ",hdet)
                hdet = hdet.replace("\n", " ")
                start = hdet.find("Storage Gate Hours")
                hours = hdet[start:len(hdet)]
                soup2 = str(soup2)
                start = soup2.find('storeCSID')
                start = soup2.find(':', start) + 3
                end = soup2.find("'", start)
                store = soup2[start:end]
                start = soup2.find('latitude')
                start = soup2.find(':', start) + 3
                end = soup2.find('"', start)
                lat = soup2[start:end]
                start = soup2.find('longitude')
                start = soup2.find(':', start) + 3
                end = soup2.find('"', start)
                longt = soup2[start:end]
            
                
                title = title.replace("?","")
                hours = hours.replace('am', ' am').replace('pm',' pm').replace('-',' - ')
                flag = True
                #logger.info(len(data))


                if flag:
                    data.append([
                        'https://www.extraspace.com',
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone,
                        "<MISSING>",
                        lat,
                        longt,
                        hours
                    ])
                    #logger.info(p,data[p])
                    p += 1
                    
            
        logger.info(".................")

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

