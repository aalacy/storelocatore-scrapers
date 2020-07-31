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
    
    url = 'https://cvsfamilyfoods.com/locations'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
    p = 0
    store_list = soup.findAll('div', {'class': 'location-data'})
    print("stores = ",len(store_list))
    for store in store_list:
        storeid = store['data-location-id']
        lat = store['data-lat']
        longt = store['data-lon']
        title = store.find('h3').text.replace('\n','').strip().split(' ',1)[1]
        link = 'https://cvsfamilyfoods.com' + store.find('h3').find('a')['href']
        street = store.find('div',{'class':'site-loc-address'}).text
        city,state = store.find('div',{'class':'site-city-state-zip'}).text.split(', ',1)
        state,pcode = state.lstrip().split(' ',1)
        phone = store.find('div',{'class':'site-loc-phone'}).text.replace('Phone: ','')
        hours = store.find('div',{'class':'site-loc-hours'}).text.replace('Hours:','')
        if title.find("Marvin") > -1:
            data.append([
                        'https://cvsfamilyfoods.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        storeid,
                        phone,
                        '<MISSING>',
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
