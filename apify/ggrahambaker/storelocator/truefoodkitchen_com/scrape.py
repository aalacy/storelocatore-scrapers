import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

session = SgRequests()
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    p = 0
    data = []
  
    url = 'https://www.truefoodkitchen.com/locations/'    
    r = session.get(url, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    maind = soup.find('div', {'class': 'type-location'})
    link_list = maind.findAll('li',{'class':'location-links'})
    print(len(link_list))    
    for link in link_list:
        try:
            link = link.find('a')['href']            
            r = session.get(link,headers = HEADERS)
            #print(link)
            soup = BeautifulSoup(r.text, 'html.parser')
            location = r.text.split('var locations = [',1)[1].split('];',1)[0]          
            location = json.loads(location)
            #print(location)
            title = location['title']
            street = location['street']
            city = location['city']
            state = location['state']
            pcode = location['zip']
            phone = location['phone']
            coord = location['geo']
            lat = coord[0]
            longt = coord[1]
            loc_id = r.text.split("momentFeedID = '" ,1)[1].split("';")[0]
            #print(loc_id)
            hourlink = 'https://momentfeed-prod.apigee.net/lf/location/store-info/'+loc_id+'?auth_token=IFWKRODYUFWLASDC'
            #print(hourlink)
            r = session.get(hourlink,headers = HEADERS).json()
            store = r['corporateId']
            hourlist = r['hours'].split(';')
            hours_map = {'1': 'Monday', '2': 'Tuesday', '3': 'Wednesday', '4': 'Thursday', '5': 'Friday', '6': 'Saturday', '7': 'Sunday'}
            hours =''
            for hr in hourlist:
                temp = hr.split(',')
                if len(temp) == 1:
                    continue
                
                day = hours_map[temp[0]]
                start = (int)(temp[1].split('00')[0])
                part = ''
                if start < 12:
                    part = ' am '
                    pass
                else:
                    start = start - 12
                    part = ' pm '
                startstr = str(start)+':00' + part
                end = (int)(temp[2].split('00')[0])
                if end < 12:
                    part = ' am '
                    pass
                else:
                    end = end - 12
                    part = ' pm '
                endstr = str(end)+':00' + part
                hours = hours + day + ' ' + startstr + '- ' + endstr + ' '
                
            if len(hours) < 3:
                hours= '<MISSING>'
            data.append([
                        'https://www.truefoodkitchen.com/',
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
                        lat,
                        longt,
                        hours
                    ])
            #print(p,data[p])
            p += 1    
            
                
          
            
            #input()
         
        except:
            pass
            
            
        
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
