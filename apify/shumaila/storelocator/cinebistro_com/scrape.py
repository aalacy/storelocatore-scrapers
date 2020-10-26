from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cinebistro_com')



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
    url = 'https://www.cmxcinemas.com/Location/GetCinemaLocations'
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()['cinemaLoc']
    for loc in loclist:
        if loc['totalcities'] == '0':
            pass
        else:
            citylist = loc['city']
            state = loc['state']
            for city in citylist:
                #logger.info(city)
                title = city['cinemaname']
                store = city['cinemaid']
                street = city['address']
                pcode = city['postalcode']
                cityn = city['locCity']
                link = 'https://www.cmxcinemas.com/Locationdetail/'+ city['slugname']
                #logger.info(link)
                r = session.get(link, headers=headers, verify=False)
                try:
                    longt,lat = r.text.split('!2d',1)[1].split('!2m',1)[0].split('!3d')
                except:
                    lat = '<MISSING>'
                    longt = '<MISSING>'
                data.append([
                            'https://www.cmxcinemas.com',
                            link,                   
                            title,
                            street,
                            cityn,
                            state,
                            pcode,
                            'US',
                            '<MISSING>',
                            '<MISSING>',
                            '<MISSING>',
                            lat,
                            longt,
                            '<MISSING>'
                        ])
                #logger.info(p,data[p])
                p += 1
                #input()
          
        
        
                
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

