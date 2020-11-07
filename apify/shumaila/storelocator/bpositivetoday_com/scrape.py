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
    pattern = re.compile(r'\s\s+') 
    url = 'https://www.bpositivetoday.com/b-positive-cherry-hill-nj'
    p = 0    
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text,'html.parser')
    divlist = soup.select_one('li:contains("Locations")').findAll('a')
    for div in divlist:
        link = 'https://www.bpositivetoday.com'+div['href']
        if link.find('#') > -1:
            continue
        if link == url:
            pass
        else:
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text,'html.parser')

        title = div.text.replace('\n',' ').strip()
        phone = soup.select_one("a[href*=tel]").text.replace('\n',' ').strip()
        address = soup.select_one("a[href*=maps]").text.replace('\n',' ').strip()
        street,city,state = address.split(', ')
        state,pcode = state.lstrip().split(' ',1)
        hours = soup.text.split('Monday',1)[1].split('*',1)[0]
        hours = re.sub(pattern,'\n',hours).replace('\n',' ').replace('day','day ')
        hours = 'Monday '+hours
        longt,lat = soup.select_one("iframe[src*=maps]")['src'].split('!2d',1)[1].split('!2m',1)[0].split('!3d')
        data.append([
                'https://www.bpositivetoday.com/',
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
   
    data = fetch_data()
    write_output(data)
   

scrape()

