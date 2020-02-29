import requests
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
    
    url = 'https://locations.crocs.com/'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    state_list = soup.findAll('div', {'class': 'itemlist'})
   # print("states = ",len(state_list))
    p = 0
    for states in state_list:
        states = states.find('a')
        #print(states.text.strip())
        states = states['href']
        r = session.get(states, headers=headers, verify=False)
        ccode = 'US'
        soup = BeautifulSoup(r.text, "html.parser")
        city_list = soup.findAll('div', {'class': 'itemlist'})
        print("cities = ",len(city_list))

        for cities in city_list:
            cities = cities.find('a')
            #print(cities.text.strip())
            cities = cities['href']
            r = session.get(cities, headers=headers, verify=False)
            
            soup = BeautifulSoup(r.text, "html.parser")
            branch_list = soup.findAll('div', {'class': 'itemlist_fullwidth'})
            #print(len(branch_list))

            for branch in branch_list:
                branch = branch.find('a')
                link = branch['href']

                r = session.get(link, headers=headers, verify=False)
                
                soup = BeautifulSoup(r.text, "html.parser")
                detail = soup.findAll('script',{'type':'application/ld+json'})
                detail = str(detail[1])
                start = detail.find('@id')
                start = detail.find(':',start)+2
                end = detail.find('"',start)
                store = detail[start:end]
                start = detail.find('streetAddress')
                start = detail.find(':',start)+2
                end = detail.find('"',start)
                street = detail[start:end]
                start = detail.find('addressLocality')
                start = detail.find(':',start)+2
                end = detail.find('"',start)
                city = detail[start:end]
                start = detail.find('addressRegion')
                start = detail.find(':',start)+2
                end = detail.find('"',start)
                state = detail[start:end]
                start = detail.find('postalCode')
                start = detail.find(':',start)+2
                end = detail.find('"',start)
                pcode = detail[start:end]
                start = detail.find('addressCountry')
                start = detail.find(':',start)+2
                end = detail.find('"',start)
                ccode = detail[start:end]
                start = detail.find('latitude')
                start = detail.find(':',start)+1
                end = detail.find(',',start)
                lat = detail[start:end]
                start = detail.find('longitude')
                start = detail.find(':',start)+1
                end = detail.find('}',start)
                longt = detail[start:end]
                longt = longt.replace('\n','')
                longt = longt.rstrip()
                start = detail.find('telephone')
                start = detail.find(':',start)+2
                end = detail.find('"',start)
                phone = detail[start:end]
                
                title = soup.find('h1').text.replace('\n','')
                title = re.sub('\s+', ' ',title).strip()
                hours = soup.find('div',{'class':'hrs'}).find('table').text.replace('\n',' ')
                hours = re.sub('\s+', ' ',hours).strip()
                hours = hours.replace('Holiday hours may vary. Please call store for details.','')
                hours = hours.replace('*','')
                hours = hours.replace('day ','day :')

                data.append([
                        'https://www.crocs.com//',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone,
                        "<MISSING>",
                        lat,
                        longt,
                        hours
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
