from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests

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
    p = 0
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    titles = []
    url = ['https://www.yogapod.com/wp-admin/admin-ajax.php?action=store_search&max_results=50&search_radius=100&autoload=1']
    for i in range(0,len(url)):
        loclist = session.get(url[i], headers=headers, verify=False).json()
        print(len(loclist))
        for loc in loclist:
            #print(loc['store'])
            if loc['store'] in titles:
                continue
            else:
                titles.append(loc['store'])
                title = loc['store']
                street = loc['address']+' ' +loc['address2']
                state = loc['state']
                city = loc['city']
                pcode = loc['zip']
                store = loc['id']
                link =  loc['url']
                lat =  loc['lat']
                longt =  loc['lng']
                hours = BeautifulSoup(loc['hours'],'html.parser').text.replace('day','day ').replace('PM','PM ').replace('Closed','Closed ')
                phone= loc['phone']
                page = session.get(link, headers=headers, verify=False)
                plist = BeautifulSoup(page.text,'html.parser').findAll('a')
                for ph in plist:
                    try:
                        if ph['href'].find('tel:') > -1:
                            phone = ph.text
                            break
                    except:
                        pass
               # print(phone)
                
                data.append([
                        'https://www.yogapod.com/',
                        link,                   
                        title.replace('\u202d',''),
                        street.replace('\u202d',''),
                        city.replace('\u202d',''),
                        state.replace('\u202d',''),
                        pcode.replace('\u202d',''),
                        'US',
                        store,
                        phone.replace('\u202d',''),
                        '<MISSING>',
                        lat,
                        longt,
                        hours.replace('\u202d','')
                    ])
                #print(p,data[p])
                p += 1
                    
            
        
        
           
        
    return data


def scrape():
    
    data = fetch_data()
    write_output(data)


scrape()
