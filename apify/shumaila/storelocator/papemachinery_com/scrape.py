from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('papemachinery_com')



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
    url = 'https://agriculture.papemachinery.com/api/locations'
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()['Locations']
   
    for loc in loclist:
        #logger.info(loc['categories'][0])
        category = loc["operatingCompanyName"]
        if category.find('Agriculture & Turf') > -1 or category.find('Construction & Forestry') > -1:
            ltype = category.replace('Papé Machinery ','')
            title = loc["title" ]
            street = loc["addressLine1"]
            try:
                street = street + ' '+loc["addressLine2"]
            except:
                pass
            city = loc['city']
            state = loc['state']
            pcode = loc['zipcode']
            store = loc['id']
            lat = loc['latitude']
            longt = loc['longitude']
            phone = loc["phoneNumber"]
            link = loc['fullUrl']
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text,'html.parser')
            logger.info(link)
            hours = soup.find('table',{'class':'simple'}).text.strip().replace('\n',' ').split('Hours')[1].lstrip()
            #logger.info(hours)
            data.append([
                'https://papemachinery.com/',
                link,                   
                title,
                street,
                city,
                state,
                pcode,
                'US',
                store,
                phone,
                ltype,
                lat,
                longt,
                hours
            ])
            logger.info(p,data[p])
            p += 1
            #input()
            
        
       
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

