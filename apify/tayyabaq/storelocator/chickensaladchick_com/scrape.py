from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('chickensaladchick_com')



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
    pattern = re.compile(r'\s\s+') 
    url = 'https://www.chickensaladchick.com/locations/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
    det = soup.find('div',{'class':'results-wrapper'})
    divlist = soup.findAll('li', {'class': 'location'})
    logger.info(len(divlist))
  
    for div in divlist:
        
        lat = div['data-latitude']
        longt = div['data-longitude']
        title = div.find('h4').text       
        #store = div['data-Loc-id']
        address =re.sub(pattern,' ',div.find('address').text)
        phone = div.find('div',{'class':'phone'}).text.replace('\n','')    
       
        address = address.lstrip()
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

        try:
            hourlist = div.find('ul',{'class':'hours'})['data-hours'].replace('[','[{').replace('][','},').replace(']','},')
            hourlist = hourlist[0:len(hourlist)-1]+']'
            hourlist =json.loads(hourlist)
            
            hours = ''
            for hr in hourlist:
                check = hr['Notes']
                opentime = hr['OpenTime'].split(':')
                start = (int)(opentime[0])
                ttype = 'am'
                if start < 12:
                    pass
                else:
                    ttype = 'pm'
                    start = start - 12
                closetime = hr['CloseTime'].split(':')
                end = (int)(closetime[0])
                ttype = 'am'
                if end < 12:
                    pass
                else:
                    ttype = 'pm'
                    end = end - 12
                midpart = str(start) + ':' + opentime[1] + " " + ttype +' - ' + str(end) + ':' + closetime[1] + " " + ttype +' '+check
                if hr['Closed'] == '1':
                    midpart = 'Closed'
                    
                hours = hours + hr['Interval'] + ' : ' +  midpart + ' '
        except:
            hours = '<MISSING>'

        link = 'https://www.chickensaladchick.com'+div['data-href']
        store = div['data-loc-id']
        if len(street) < 4:
            street = '<MISSING>'
        data.append([
                        'https://www.chickensaladchick.com/',
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
                        lat,
                        longt,
                        hours.rstrip()
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
