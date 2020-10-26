from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('firehousesubs_com')



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
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    p = 0

    for statenow in states:
        url = 'https://www.firehousesubs.com/FindLocations/GetLocationsByState/?state='+statenow
        loclist = session.get(url, headers=headers, verify=False).json()
        #logger.info(loclist)
        for loc in loclist:            
            if str(loc['isComingSoon']) == 'False':
                try:
                    street = loc['address'] + ' '+loc['address2']
                except:
                    street = loc['address']
                    
                city = loc['city']
                state = loc['state']
                lat = loc['latitude']
                longt = loc['longitude']
                phone = loc['phone'].replace('\u200b','').replace('\u202c','')
                link = loc['moreInfoUrl']
                pcode = loc['zip']
                hours1 = loc['hoursOpen']
                title = loc['title']
                store = loc["siteId"]
                ccode = 'US'
                if phone.lower().find('available') > -1 or len(phone) < 3 :
                    phone = '<MISSING>'
                try:
                    if len(hours1) < 3:
                        hours1 = '<MISSING>'
                except:
                    hours1 = '<MISSING>'

                try:
                    if len(store) < 1:
                        store = '<MISSING>'
                except:
                    store = title.split('#')[1]
                r = session.get(link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text,'html.parser')
                hours = ''
                try:
                    hourlist = soup.find('div',{'class':'hours'}).findAll('li')
                    for hr in hourlist:
                        hours = hours + hr.findAll('span')[0].text + ' ' +hr.findAll('span')[1].text + ' '
                except:
                     hours = hours1
                     
                if len(hours) < 3:
                    hours = hours1      
                
        
                data.append([
                'https://www.firehousesubs.com/',
                link,                   
                title,
                street,
                city,
                state,
                pcode,
                ccode,
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

