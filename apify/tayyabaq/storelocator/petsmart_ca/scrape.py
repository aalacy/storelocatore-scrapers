import csv
import os
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re, time
import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('petsmart_ca')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()

def fetch_data():
    data = []
    store_links =[]
    clear_links =[]
    #CA stores
    url = 'https://www.petsmart.ca/stores/ca/'
    u='https://www.petsmart.ca/'
    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    store=soup.find('div',class_='all-states-list container')
    str=store.find_all("a")
    for i in str:
        newurl=i['href']
        page = session.get(newurl)
        soup = BeautifulSoup(page.content, "html.parser")
        store=soup.find_all('a', class_='store-details-link')
        for j in store:

            ul=u+j['href']
            #logger.info(ul)
            page = session.get(ul)
            soup = BeautifulSoup(page.content, "html.parser")
            div = soup.find('div',class_='store-page-details')
            try:
              loc = div.find('h1').text
              if "closed" in loc.lower():
                continue
            except:
               continue
            ph=div.find('p',class_='store-page-details-phone').text.strip()
            addr=div.find('p',class_='store-page-details-address').text.strip().split("\n")
            #logger.info(addr)
            if len(addr) ==2:
                street=addr[0]
                addr=addr[1].strip().split(',')
            elif len(addr)>2:
                add=addr[-1]
                del addr[-1]
                street=" ".join(addr)
                addr=add.strip().split(',')
            
            cty=addr[0]
            addr=addr[1].strip().split(' ')
            sts=addr[0]
            del addr[0]
            zcode=" ".join(addr).strip()
            try:
                hours=soup.find('div',class_='store-page-details-hours-mobile visible-sm visible-md ui-accordion ui-widget ui-helper-reset').text
            except:
                hours=soup.find('div',class_='store-page-details-hours-mobile visible-sm visible-md').text
            hours=hours.strip().replace('\n\n','').replace('\n','')
            for day in ['MON','TUE','THU','WED','FRI','SAT','SUN']:
                if day not in hours:
                    hours=hours.replace('TODAY',day)
            lat,long=re.findall(r'center=([\d\.]+),([\-\d\.]+)',soup.find('div',class_='store-page-map mapViewstoredetail').find('img').get('src'))[0]
            #logger.info(lat,long)
            
            
            """try:
                loc=soup.find('h1', class_ ='store-name').text
            except:
                logger.info("closed")
            else:
                street = soup.find('div', itemprop='streetAddress').text
                city = soup.find('span',itemprop='addressLocality')
                cty=city.text
                sts = city.find_next('span',itemprop='addressLocality').text
                zcode = soup.find('span',itemprop='postalCode').text
                num=j['id']
                ph=soup.find("a",class_="store-contact-info").text
                lat=soup.find("meta",itemprop='latitude')['content']
                lng=soup.find("meta",itemprop='longitude')['content']
                hr=soup.find_all("span",itemprop="dayOfWeek")  
                op=soup.find_all("time",itemprop='opens')
                cl=soup.find_all("time",itemprop='closes')
                DY=['SUN','MON','TUE','WED','THU','FRI','SAT']
                hours=""
                for k in range(0,len(op)) :
                    hours+=hr[k].text+" "
                    if hr[k].text != 'TODAY':
                        DY.remove(hr[k].text)
                    hours+=op[k]['content']+"-"
                    hours+=cl[k]['content']+" "
                hours=hours.replace("TODAY",DY[0])
                hours=hours.replace("-null","")
                logger.info(hours)"""
            data.append([
                    'https://www.petsmart.ca/',
                     ul.replace(u'\u2019',''),
                    loc.replace(u'\u2019','').strip(),
                    street.replace(u'\u2019',''),
                    cty.replace(u'\u2019',''),
                    sts.replace(u'\u2019',''),
                    zcode.replace(u'\u2019',''),
                    'US'.replace(u'\u2019',''),
                    j['id'].replace(u'\u2019',''),
                    ph.replace(u'\u2019',''),
                    '<MISSING>',
                    lat,
                    long,
                    hours.replace(u'\u2019','')
                    ])
         
    return data
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
