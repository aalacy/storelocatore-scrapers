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
    p= 0
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.campbowwow.com/locations/'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.find('ul',{'class':'results'}).findAll('li')#soup
    for div in divlist:
        link = 'https://www.campbowwow.com' + div.select_one('a:contains("Website")')['href']
        title = div.find('span',{'class':'location-name'  }).text
        address = div.find('address').text
        address = re.sub(pattern,'\n',address).strip().splitlines()
        street = address[0].replace('\xa0',' ')
        try:
            city,state = address[1].split(', ',1)
        except:
            city,state = address[0].split(', ',1)
            street = '<MISSING>'
            
        state,pcode = state.lstrip().split(' ',1)
        ccode = 'US'
        phone = div.find('a',{'class':'phone'}).text        
        store = div['data-loc-id']
        lat = div['data-latitude']
        longt = div['data-longitude']
        #print(link)
        r = session.get(link, headers=headers, verify=False)   
        soup =BeautifulSoup(r.text, "html.parser")
        try:
            hours = soup.find('ul',{'id':'LocalHoursBlock'}).text
            hours = re.sub(pattern,'\n',hours).strip().split('View')[0].replace('\n',' ')
        except:
            continue
        if len(pcode) > 5:
            ccode = 'CA'
            
        data.append([
                        'https://www.campbowwow.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        ccode,
                        store,
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
