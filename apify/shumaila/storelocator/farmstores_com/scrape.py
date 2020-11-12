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
    titlelist = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'http://www.farmstores.com/wp-admin/admin-ajax.php?action=store_search&lat=33.749&lng=-84.38798&max_results=25&search_radius=50&autoload=1'
    loclist = session.get(url, headers=headers, verify=False).json()
    for loc in loclist:
        street = loc['address']
        
        city = loc['city']
        state = loc['state']
        pcode = loc['zip']
        title = loc['store']
        phone = loc['phone']
        lat = loc['lat']
        longt = loc['lng']
        store = loc['id']
        link = loc['permalink']
        hours = loc['hours']
        flag = 0
        street1 = ''
        try:
            street1 = street
            street = street1.split(',')[0]
            flag = 1
            
            
                
        except:
            street1 = ''
            pass
        if len(state) < 2 and flag == 1:
            try:
                state = street1.split(',')[-1].lstrip().split(' ',1)[0]
            except:
                pass
        if len(pcode) < 2 and flag == 1 :
            try:
                pcode = street1.split(',')[-1].lstrip().split(' ',1)[1]
            except:
                pass
        
        if len(state) < 2:
            state = '<MISSING>'
        if len(pcode) < 2:
            pcode = '<MISSING>'
        if pcode.isdigit():
            pass
        else:
            pcode = '<MISSING>'
        try:
            hours = BeautifulSoup(hours,'html.parser').text.replace('day','day ').replace('PM','PM ')
        except:
            hours = '<MISSING>'
        if len(phone) < 2:
            phone = '<MISSING>'
        if link.find('coming-soon') > -1 or title in titlelist:
            continue
        if 'Pennsylvania' in state:
            state = 'PA'
        titlelist.append(title)
        data.append([
                        'http://www.farmstores.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone,
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        hours
                    ])
       
        p += 1
                
            
      
        
    return data


def scrape():
   
    data = fetch_data()
    write_output(data)
  

scrape()
