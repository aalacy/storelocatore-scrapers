from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('quiklendcash_com')



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
    cleanr = re.compile(r'<[^>]+>')    
    pattern = re.compile(r'\s\s+')    
    url = 'https://quiklendcash.com/store-locations/'
    p = 0
    loclist = session.get(url, headers=headers, verify=False).text
    cleanr = re.compile(r'<[^>]+>')
    loclist = re.sub(cleanr, '',str(loclist))
    loclist = re.sub(pattern, ' ',str(loclist))
    loclist = loclist.split('location_data.push(',1)[1].split('map_0 = wpseo')[0]
    loclist = loclist.replace(', } );','},').replace('location_data.push( ','')
    loclist = '[' + loclist +']'
    loclist = loclist.replace(', ]',']').replace("'",'"')
    #logger.info("temp",loclist)          
   
    loclist = json.loads(loclist)
    #logger.info("json",loclist)  
    for loc in loclist:
        title = loc['name']
        address = loc['address']
        phone = loc['phone']
        lat = loc['lat']
        longt = loc['long']
        link = loc['self_url']
        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        
        try:
            r = session.get(link, headers=headers, verify=False).text
            soup = BeautifulSoup(r, "html.parser")
            hourlist = soup.find('table',{'class':'wpseo-opening-hours'})
            daylist = hourlist.findAll('td',{'class':'day'})
            timelist = hourlist.findAll('td',{'class':'time'})
            hours = ''
            for i in range(0,len(daylist)):
                hours = hours + daylist[i].text + ' : ' + timelist[i] .text+ ' '
        except Exception as e:
            logger.info(e)
            hours = '<MISSING>'
        data.append([
                'https://quiklendcash.com/',
                link,                   
                title,
                street.lstrip(),
                city.lstrip().replace(',',''),
                state.lstrip(),
                pcode.lstrip(),
                'US',
                '<MISSING>',
                phone,
                '<MISSING>',
                lat,
                longt,
                hours,
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

