import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import html
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
    # Your scraper here
    data = []
    p = 0
    url = "https://www.pridestaff.com/wp-admin/admin-ajax.php"
    req_data = {"action": "get_locations_ajax"}
    r = session.post(url, data=req_data)
    cleanr = re.compile(r'<[^>]+>')
    r.raise_for_status()
    data_dict = r.json()
    #print(data_dict)
    for location in data_dict:
        #print(location)
        lat = location['coord']['lat']
        longt = location['coord']['lng']
        det = location['info']
        soup = BeautifulSoup(str(det),'html.parser')
        title = soup.find('strong').text
        link = soup.find('a')['href']        
        soup = str(det)
        start = soup.find('<br>')       
        end = soup.find('<a',start)
        address = soup[start:end]
        start = address.find('>')+1
        end = address.find('<',start)
        street = address[start:end]
        start = end + 1
        start = address.find('>',start)+1
        end = address.find('<',start)

        #print(address[start:end])
        try:
            city,state = address[start:end].split(', ',1)
        except:
            street = street + ' '+ address[start:end]
            
            start = end + 1
            start = address.find('>',start)+1
            end = address.find('<',start)
            print(address[start:end])
            city,state = address[start:end].split(', ',1)
            
            
        state = state.lstrip()
        state,pcode = state.split(' ',1)
        if street.lower().find('coming') == -1:
            r = session.get(link)
            soup = BeautifulSoup(r.text,'html.parser')
            try:
                phone = soup.find('ul',{'class':'location-contact'}).find('a')['href']
            except:
                phone='<MISSING>'
            phone = phone.replace('tel:','').replace('.','-')
            
        #print(link)
        if street.lower().find('coming') == -1:
            data.append([
                            'https://www.pridestaff.com/',
                            link,                   
                            title,
                            street,
                            city.lstrip(),
                            state.lstrip(),
                            pcode.lstrip(),
                            'US',
                            '<MISSING>',
                            phone,
                            '<MISSING>',
                            lat,
                            longt,
                            '<MISSING>'
                        ])
            #print(p,data[p])
            p += 1
        
        
        
        

        
       
        
   
    
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
