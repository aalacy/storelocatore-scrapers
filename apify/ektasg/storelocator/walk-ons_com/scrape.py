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
    
    url = 'https://walk-ons.com/locations'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('div', {'class': 'locationList'})
   # print("states = ",len(state_list))
    p = 0
    for div in divlist:        
        loclist = div.findAll('div', {'class': 'locationItem'})
        for loc in loclist:
            link = loc.find('a')['href']
            if link.find('locations.walk-ons.com') == -1:
                continue
            print(link)
            r = session.get(link, headers=headers, verify=False)
            soup =BeautifulSoup(r.text, "html.parser")
            title = soup.find('div',{'class':'Location-Name'}).text
            street = soup.find('span',{'class':'c-address-street-1'}).text
            city = soup.find('span',{'class':'c-address-city'}).text
            state = soup.find('span',{'class':'c-address-state'}).text
            pcode = soup.find('span',{'class':'c-address-postal-code'}).text
            try:
                phone = soup.find('span',{'class':'phone-text'}).text
            except:
                phone = '<MISSING>'
            try:
                hours = soup.find('table',{'class':'hours'}).text.replace('PM','PM ').replace('Day of the Week','').replace('Closed','Closed ').replace('Hours','').replace('day','day ')
            except:
                hours = '<MISSING>'
                
            lat = str(soup).split('lat: ',1)[1].split(',',1)[0]
            longt = str(soup).split('lng: ',1)[1].split(',',1)[0]           
            if len(hours) < 3:
                hours = '<MISSING>'  
            data.append([
                        'https://walk-ons.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
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
