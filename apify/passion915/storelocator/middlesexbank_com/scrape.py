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
    # Your scraper here
    data = []
    pattern = re.compile(r'\s\s+')
    url = 'https://www.middlesexbank.com/locations'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    state_list = soup.findAll('div', {'class': 'itemlist'})  
    p = 0
    store_list = soup.find_all('li',{'class':'branch'})
    print(len(store_list))
    for store_item in store_list:        
        test = store_item.find('a',{'class':'ext'})       
            
        address = store_item['data-address']
        lat = store_item['data-lat']
        longt = store_item['data-lng']        
        location_name = store_item.find('a',{'class':'location-title'}).text
        #link = 'https://www.middlesexbank.com' + store_item.find('a',{'class':'visit-page'})['href']
        # if str(str(address).split(' ')[len(str(address).split(' ')) - 2]).strip() == 'MA':
        street,city = address.split(', ',1)
        city,state,pcode = city.lstrip().split(' ',2)        
        country_code = "US"
        #city = str(address.split(',')[1]).replace(zip,'').replace(state,'').strip()        
        store_number = "<MISSING>"
        if test is None:
            locator_domain = 'https://www.middlesexbank.com' + store_item.find('a',{'class':'visit-page'})['href']
            r = session.get(locator_domain, headers=headers, verify=False)                
            href_data =BeautifulSoup(r.text, "html.parser")   
            phone = href_data.find('span',{'property':'telephone'}).a.text        
            hours_of_operation = href_data.find('div',{'property':'openingHours'}).text.strip()
            ltype = 'Branch | ATM'
            hours_of_operation = hours_of_operation.replace('\r',' ').replace('\n',' ')
            hours_of_operation = re.sub(pattern, ' ', hours_of_operation)
            try:
                hours_of_operation = hours_of_operation.split('Drive')[0]
            except:
                pass
        else:            
            ltype = 'ATM'
            phone = '<MISSING>'
            hours_of_operation = '<MISSING>'
            locator_domain= '<MISSING>'           
    
        data.append([
                        'https://www.middlesexbank.com',
                        locator_domain,                   
                        location_name,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store_number,
                        phone,
                        ltype,
                        lat.lstrip(),
                        longt.lstrip(),
                        hours_of_operation
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
