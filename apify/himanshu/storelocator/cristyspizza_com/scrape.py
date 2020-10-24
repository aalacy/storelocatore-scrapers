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
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://cristyspizza.com/'
    r = session.get(url, headers=headers, verify=False)
    
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.select_one('li:contains("Store Locations")').select("a[href*=location]")
   # print("states = ",len(state_list))
    p = 0
    for div in divlist:
        link = div['href']
        #print(link)
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text,'html.parser')
        content = soup.findAll('div',{'class':'fl-html'})[0].findAll('p')
        try:
            coord = soup.findAll('div',{'class':'fl-html'})[1].find('iframe')['src']
        except:
            coord = soup.findAll('div',{'class':'fl-html'})[2].find('iframe')['src']
        address = content[0].text.splitlines()
        street = address[0]
        city, state =address[1].split(', ',1)
        state, pcode = state.lstrip().split(' ',1)
        phone = content[1].text
        hours = content[2].text.replace('\n',' ')
        title = soup.find('h1').text.replace('\n','').split()
        lat,longt = coord.split('!2d',1)[1].split('!2m',1)[0].split('!3d')
        
        data.append([
                        'https://cristyspizza.com/',
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
