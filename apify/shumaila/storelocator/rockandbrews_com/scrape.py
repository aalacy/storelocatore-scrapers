from bs4 import BeautifulSoup
import csv
import string
import re, time, json

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rockandbrews_com')



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
    p = 0
    pattern = re.compile(r'\s\s+') 
    url = 'https://www.rockandbrews.com/locations'
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split('"galleryImages":[],"locations":[{"',1)[1].split('}],"menus":[]',1)[0]
    loclist = '[{"' + r + '}]'   
    loclist = json.loads(loclist.replace("'",'"'))
    for loc in loclist:
        #logger.info(loc)
        store = loc['id']
        city = loc['city']
        ccode = loc['country']
        title = loc['name']
        phone = loc['phone']
        lat = loc['lat']
        longt = loc['lng']
        pcode = loc['postalCode']
        street = loc['streetAddress']
        state = loc['state']
        hourlist = loc['schemaHours']
        check = loc['customLocationContent']
        if check.find('Coming Soon') > -1 or ccode == 'MX':
            continue
        link = 'https://www.rockandbrews.com/'+loc['slug']
        #logger.info(title,link)
        hours= ''
        try:
            for hr in hourlist:            
                endtime =(int)(hr.split('-')[1].split(':')[0])
                if endtime > 12:
                    endtime = endtime-12
                hours = hours + hr.split('-')[0]+ 'am - ' + str(endtime) +':'+ hr.split('-')[1].split(':')[1] + ' pm '
        except:
            hours = '<MISSING>'
        try:
            phone = phone[0:3]+'-'+phone[3:6]+'-'+phone[6:10]
        except:
            phone = '<MISSING>'
        data.append([
                        'https://www.rockandbrews.com',
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
