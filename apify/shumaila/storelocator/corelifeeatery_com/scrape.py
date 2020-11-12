from bs4 import BeautifulSoup
import csv
import string
import re, time,json

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
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.corelifeeatery.com/sitemap.xml'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")      
    divlist = soup.findAll('loc')
    titlelist = []
    p = 0
    for div in divlist:
        if div.text.find('locations') > -1:
            #print(div.text)
            r = session.get(div.text, headers=headers, verify=False)
            soup =BeautifulSoup(r.text, "html.parser")
            linklist = soup.findAll('loc')
            for link in linklist:
                link = link.text
                #print(link)
                r = session.get(link, headers=headers, verify=False)
                soup =BeautifulSoup(r.text, "html.parser")
                title = soup.find('h1').text
                if title.find('Opening Soon!') > -1:
                    continue
                hours = soup.text.split('Hours:',1)[1].lstrip().split('Features',1)[0].replace('\n',' ').strip()
                longt,lat = soup.find('iframe')['src'].split('!2d',1)[1].split('!2m',1)[0].split('!3d',1)
                try:
                    lat = lat.split('!',1)[0]
                except:
                    pass
                address = r.text.split('"address":',1)[1].split('},',1)[0]
                address = address+'}'
                address = json.loads(address)                
                street = address['streetAddress']
                city= address['addressLocality']
                state=address['addressRegion']
                pcode= address['postalCode']
                ccode = address['addressCountry']
                store = r.text.split('article id="post-',1)[1].split('"',1)[0]
                if title in titlelist:
                    continue
                titlelist.append(title)
                data.append([
                        'https://www.corelifeeatery.com',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        '<MISSING>',
                        '<MISSING>',
                        lat,
                        longt,
                        hours
                    ])
                #print(p,data[p])
                p += 1
                #input()
                
                
            
        
    return data


def scrape():    
    data = fetch_data()
    write_output(data)
   
scrape()
