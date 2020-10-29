from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('imxpilates_com')



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
    url = 'https://imxpilates.com/studios.php'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.findAll('div', {'class': 'studionewcol'})
    #logger.info("states = ",len(divlist))
    p = 0
    titles = []
    titles.append('None')
    for div in divlist:
        div = div.findAll('p')
        for repo in div:
            linklist = repo.findAll('a')
            for link in linklist:
                try:
                    title = link.text.replace('IM=X®','').lstrip().replace('\n','')
                    link = link['href']
                    if len(title) < 2:
                        title = link.split('imxpilates',1)[1].split('.',1)[0]
                    #logger.info(title,link)
                    if (link.find('branch') > -1 or link.find('imx') > -1 )and title.find('Coming Soon') == -1 and title not in titles:
                        titles.append(title)
                        #logger.info(p,link)                       
                        r = session.get(link, headers=headers, verify=False)                    
                        soup =BeautifulSoup(r.text, "html.parser")                        
                        det = soup.find('div',{'class':'header-left'}).text                        
                        det = re.sub(pattern,'\n',det).splitlines()                        
                        count = len(det)
                        phone = det[count - 1].lstrip()                        
                        address = ' '.join(det[0:count-1]).lstrip()
                        #logger.info(address)
                        check = ''
                        try:
                            check = address.split('(')[1].split(')')[0]
                            
                            check = ' ('+ check +')'
                            address =address.replace(check,'')
                            #logger.info(address)
                        except :
                            pass
                        try:
                            address = address.split('!',1)[1]
                        except:
                            pass
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
                            
                        #logger.info(address)
                        
                        street = street + ' ' + str(check)               
                        store = str(soup).split('?studioid',1)[1].split('&',1)[0]
                        try:
                            store = store.split('studioid=',1)[1]
                        except:
                            pass
                        
                        if city.find('Tampa') > -1 and title.find('Carrollwood') > -1:
                            city = title
                            street = street + ' Tampa'
                            state = state.lstrip().split(' ')[0]
                            pcode = pcode.lstrip().split(' ')[0]
                        if len(title) < 3:
                            title = city.lstrip().replace(',','')
                            titles.append(title)
                        data.append([
                        'https://www.imxpilates.com/',
                        link,                   
                        title,
                        street.lstrip().replace(',',''),
                        city.lstrip().replace(',',''),
                        state.lstrip().replace(',',''),
                        pcode.lstrip().replace(',',''),
                        'US',
                        store,
                        phone,
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>'
                        ])
                        #logger.info(p,data[p])
                        p += 1
                    #input()
                        
                except Exception as e:
                    #logger.info(e)
                    pass
            
         
            
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
