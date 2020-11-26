from bs4 import BeautifulSoup
import csv
import string
import re, time, json

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
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.dallasbbq.com/'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.find('nav').findAll('div')[1].findAll('a')  
    p = 0
    for div in divlist:
        if 'menus' in div['href']:
            continue
        link = 'https://www.dallasbbq.com'+div['href']
        r = session.get(link, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        title = soup.find('h2').text
        content = soup.find('div',{'class':'sqs-block-content'})
        content = re.sub(cleanr,'\n',str(content))
        address = re.sub(pattern,'\n',str(content)).lstrip().splitlines()
        title = address[0]
        street = address[1]
        city,state = address[2].split(', ',1)
        state,pcode = state.lstrip().split(' ',1)
        hours = content.split('Hours',1)[1].split('Phone',1)[0]
        hours = hours.replace('\n',' ').strip().replace('&amp;','-')
        phone = content.split('Phone',1)[1].replace('\n','')
        mapc = soup.find('div',{'class':'sqs-block-map'})['data-block-json']   
        mapc = json.loads(mapc)
        lat = mapc['location']['mapLat']
        longt = mapc['location']['mapLng']
        try:
            phone = phone.split('Order',1)[0]
        except:
            pass
        data.append([
                        'https://www.dallasbbq.com/',
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
