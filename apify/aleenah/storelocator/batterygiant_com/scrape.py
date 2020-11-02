import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('batterygiant_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()
all=[]

def fetch_data():
    # Your scraper here


    res=session.get("https://www.batterygiant.com/sitemap.htm")
    soup = BeautifulSoup(res.text, 'html.parser')
#    logger.info(soup)
    sa = soup.find_all('td', {'class': 'storeLink'})
    tims=soup.find_all('td', {'width': '206'})
    logger.info(len(sa))
    for a in sa:
        url = "https://www.batterygiant.com"+a.find('a').get('href')

        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        #logger.info(soup)
        #logger.info(re.findall('Hour.*',str(soup))[0])


        loc=soup.find('div', {'class': 'grid_92'}).find('h1').text
        divs = soup.find_all('div', {'style': 'width:200px; float:left;'})
        #logger.info(len(divs))
        addr=divs[0].text.replace('Address:','').replace('\r','').strip().split('\n')
        csz=addr[-1]
        del addr[-1]
        street = ' '.join(addr)
        csz=csz.split(',')
        city=csz[0]
        zip=re.findall(r'[\d]{5}',csz[1])
        if zip==[]:
            state=csz[1].strip()
            zip="<MISSING>"
        else:
            zip=zip[0]
            state=csz[1].replace(zip,'').strip()
        if 'Panama' in state:
            continue
        phone=re.findall(r'Phone:([\d\-]+)',divs[1].text.replace('\n',''))
        if phone==[]:
            phone="<MISSING>"
        else:
            phone=phone[0]

        tim=soup.find('div', {'style': 'float:left; padding:8px; padding-top:0px;'}).prettify().replace('<p>','').replace('</p>','').replace('</div>','').replace('</span>','').replace('<span style="font-weight:bold;">','').replace('<strong>','').replace('Hours:','').replace('<br/>','').replace('</strong>','').replace('<div style="float:left; padding:8px; padding-top:0px;">','').replace('\n',' ').strip()
        tim=re.sub(r'[ ]+',r' ',tim)
        if tim=="":
            tim="<MISSING>"
        if 'Closed. Thank you for your business.' in tim:
            continue

        lat,long=re.findall(r'LatLng\((.*),(.*)\)',str(soup))[0]




        all.append([
            "https://www.batterygiant.com/sitemap.htm",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim,  # timing
            url])



    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
