from bs4 import BeautifulSoup
import csv
import string,usaddress
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
               
                content = soup.text.split('Location:',1)[1].split('Get Directions',1)[0].strip()
                content1 = content.splitlines()
                #print(content)
                m = 0                
                
                phone = content1[-1]
                address = content.replace(phone,'').replace('\n',' ').strip()
                try:
                    address = address.split('Located',1)[0]
                except:
                    pass
                try:
                    address = address.split('In the same',1)[0]
                except:
                    pass
                try:
                    address = address.split('Across',1)[0]
                except:
                    pass
                try:
                    address = address.split('Near',1)[0]
                except:
                    pass
                address = usaddress.parse(address)

                i = 0
                street = ""
                city = ""
                state = ""
                pcode = ""
                while i < len(address):
                    temp = address[i]
                    if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find('Occupancy') != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                        street = street + " " + temp[0]
                    if temp[1].find("PlaceName") != -1:
                        city = city + " " + temp[0]
                    if temp[1].find("StateName") != -1:
                        state = state + " " + temp[0]
                    if temp[1].find("ZipCode") != -1:
                        pcode = pcode + " " + temp[0]
                    i += 1

                street = street.lstrip().replace(',','')
                city = city.lstrip().replace(',','')
                state = state.lstrip().replace(',','')
                pcode = pcode.lstrip().replace(',','')
                try:
                    state = state.split(' ',1)[0]
                except:
                    pass
                try:
                    pcode = pcode.split(' ',1)[0]
                except:
                    pass
                try:
                    city = city.split('(')[0].split(' ')[-1]
                except:
                    pass
                                
                store = r.text.split('article id="post-',1)[1].split('"',1)[0]
                if link in titlelist:
                    continue
                titlelist.append(link)
                city = link.split('locations/',1)[1].split('-'+state.lower(),1)[0]
                city = city.replace('-',' ').strip()
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
                        phone.replace('Phone:','').strip(),
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
