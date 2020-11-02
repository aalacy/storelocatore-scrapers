from bs4 import BeautifulSoup
import csv
import string
import re, time
import sgzip, json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('habitat_org__restores')



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
    MAX_RESULTS = 20  # max number of results the website gives
    MAX_DISTANCE = 50.0  # max number of distance from the zip it covers
    data = []
    p = 0
    pattern = re.compile(r'\s\s+')
    search = sgzip.ClosestNSearch()
    search.initialize()
    query_coord = search.next_zip()   
    titlelist = []
    titlelist.append('none')
    while query_coord:
        count = 0
        result_coords = []
        url = 'https://www.habitat.org/local/restore?zip=' + query_coord
        #logger.info(url)
        r = session.get(url, headers=headers, verify=False)
        try:
            loclist = r.text.split('"markers":',1)[1].split('}],',1)[0]
            loclist =json.loads(loclist)
            #logger.info(len(loclist))
            for loc in loclist:
                #logger.info(loc)
                title = loc['title']
                lat = loc['position']['lat']
                longt =  loc['position']['lng']
                address= loc['details']['desc']
                address = BeautifulSoup(address,'html.parser')
                address = address.findAll('p')
                #logger.info(len(address))
                if len(address) == 0:
                    continue
                if len(address) == 2:
                    street =address[0].text
                    #city,state = address[-1].text.split(', ')
                elif len(address) == 3:
                    street =address[0].text + ' ' +address[1].text
                    #city,state = address[-1].text.split(', ')
                elif len(address) == 4:
                    street =address[0].text + ' ' +address[1].text+ ' ' +address[2].text

                try:
                    city,state = address[-1].text.split(', ')
                except:
                    pass
                state,pcode = state.lstrip().split(' ',1)                
                phone = loc['details']['phone'].replace('tel:+1','')
                link = loc['details']['website']
                if len(phone) > 8:
                    phone = phone[0:3]+'-'+phone[3:6]+'-'+phone[6:10]
                else:
                    phone = '<MISSING>'

               
                if pcode.find('-') > -1 or pcode.isdigit():
                    ccode = 'US'
                else:
                    ccode = 'CA'
                   
                    
                if len(link)  < 3:
                    link = url
                if title in titlelist:
                    pass
                else:
                    titlelist.append(title)
                    data.append([
                            'https://www.habitat.org/restores',
                            link,                   
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            ccode,
                            '<MISSING>',
                            phone,
                            '<MISSING>',
                            lat,
                            longt,
                            '<MISSING>'
                        ])
                    #logger.info(p,data[p])
                    p += 1
                    #input()
                
                
        except Exception as e:
            #logger.info(e)
            #input()
            pass
        
        search.max_distance_update(MAX_DISTANCE)
        '''elif count == MAX_RESULTS:  # check to save lat lngs to find zip that excludes them
            logger.info("max count update")'''
        search.max_count_update(result_coords)
        #else:
         #   logger.info("oops! the maxcount should be", count)
          #  raise Exception("expected at most " + MAX_RESULTS + " results")

        query_coord = search.next_zip()
  
        
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
