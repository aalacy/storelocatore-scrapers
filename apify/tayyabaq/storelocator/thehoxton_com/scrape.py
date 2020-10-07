from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
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
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://thehoxton.com/'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text,'html.parser')
    linklist = soup.find('nav',{'class':'nav-container__locations-nav'}).findAll('a')
    for link in linklist:       
        if link.text.find('coming') == -1:
            #print(link)
            title = link.text
            try:
                link = link['href']
            except:
                continue            
            r = session.get(link, headers=headers, verify=False)
            if r.text.find(', USA') == -1:
                continue
            else:
                soup = BeautifulSoup(r.text,'html.parser').text
                address = soup.split('Find Us',1)[1].split(', USA')[0]
                street , city, state = address.split(', ')
                state,pcode = state.lstrip().split(' ',1)
                phone = r.text.split('please call ',1)[1].split('<',1)[0].replace('.','').replace('+1','')
                #print(phone)
                data.append([
                'https://thehoxton.com/',
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
                '<MISSING>',
                '<MISSING>',
                '<MISSING>'
                ])
                print(p,data[p])
                p += 1
        
            


    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

