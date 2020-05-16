import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
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
    
    
    url = 'https://freddysusa.com/locations-list/'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    store_list = soup.findAll('div', {'class': 'locationSearchResult'})
   # print("states = ",len(state_list))
    p = 0
    for store in store_list:
        street = ""
        state = ""
        city = ""
        pcode = ""       
        store = store.find('a')
        if store.text.find("COMING SOON") == -1:
        #print(states.text.strip())
            link= 'https://freddysusa.com/store/'+store['href']
            r = session.get(link, headers=headers, verify=False)
            ccode = 'US'
            soup = BeautifulSoup(r.text, "html.parser")
            coming = soup.findAll('img')
            flag = 0
            for mn in coming:
                if mn['src'].find('coming-soon-restaurant') > -1:
                    flag = 1
                    break
            if flag == 0:
                title = soup.find('p',{'class':'storeName'}).text
                address = str(soup.find('p',{'class':'storeAddress'}))
                #print(address)
                start = address.find('>')+ 1
                end = address.find('<',start)
                street = address[start:end]
                start = address.find('>',end)+ 1
                end = address.find('<',start)
                address = address[start:end]
                city,address = address.split(',',1)
                address = address.lstrip()
                state,pcode = address.split(' ',1)
                
                #print(city,state,pcode)   
                try:
                    phone = soup.find('p',{'class':'storePhone'}).text
                except:
                    phone = '<MISSING>'
                    
                hourlist = soup.findAll('p',{'class':'storeHours'})

                hours= ''
                for hr in hourlist:
                    hours = hours + hr.text + ' '
                
                hours = hours.replace('day', 'day ')
                if len(street) < 2:
                    street = 'N/A'
                
               
                street = street.strip()
                pcode = pcode.strip()
                city = city.strip()
                state= state.strip()
                phone = phone.strip()
                if len(phone) < 2:
                    phone = '<MISSING>'
                if len(hours) < 2:
                    hours = '<MISSING>'
                    
                data.append(['https://freddysusa.com/',link,title,street,city,state,pcode,'US',"<MISSING>",phone,"<MISSING>","<MISSING>","<MISSING>",hours])
                #print(p,data[p])
                #input()
                p += 1
                

                
                
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
