from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('nicknwillys_com')



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
    url = 'https://nicknwillys.com/locations/'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text,'html.parser')
    divlist = soup.findAll('div',{'class':'et_pb_text_inner'})
    for div in divlist:
        det = re.sub(cleanr,' ',str(div)).splitlines()
        coord = div.find('a')['href']
        coord = coord.split('@')[1].split('/data')[0]
        lat, longt = coord.split(',',1)
        longt = longt.split(',',1)[0]
        #logger.info(det)        
        title = det[0].lstrip()
        address = det[1].lstrip()
        if address.find('MAP') > -1:
            address = address.split(' MAP')[0]
            #logger.info("YES")
            phone = det[2].lstrip().split(' ',1)[1].rstrip()
        else:
            phone = det[3].lstrip().split(' ',1)[1].rstrip()        
       
        address = usaddress.parse(address.strip())
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                    temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
    
    
        data.append([
                'https://nicknwillys.com/',
                'https://nicknwillys.com/locations/',                   
                title.strip(),
                street.lstrip(),
                city.lstrip().replace(',',''),
                state.lstrip(),
                pcode.lstrip(),
                'US',
                '<MISSING>',
                phone.strip(),
                '<MISSING>',
                lat,
                longt,
                '<MISSING>'
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

