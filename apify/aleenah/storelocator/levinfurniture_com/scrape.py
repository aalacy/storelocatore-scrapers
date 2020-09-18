import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain",'page_url', "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    # Your scraper here
    data = []
    dup = []
    dup.append('none')
    p = 0
    res1=session.get("https://www.levinfurniture.com/api/rest/pages/contacts", headers={'content-type': 'application/json'}, verify=False).json()['content']
    #print(res1)
    soupt = BeautifulSoup(res1,'html.parser')
    linklist = soupt.findAll('avb-link')
    for link in linklist:
        try:
            link = link['data-href']
            if link.find('/locations') > -1:
                nowlink = link.split('/locations/',1)[1]
                nowlink = 'https://www.levinfurniture.com/api/rest/pages/locations%2F'+nowlink
                r = session.get(nowlink, headers={'content-type': 'application/json'}, verify=False).json()
                try:
                    store = r['page_id']
                    #print(store)
                except:
                    store = '<MISSING>'
                r = r['content']
                soup = BeautifulSoup(r,'html.parser')
                #print(nowlink)
                title =soup.find('h2').text.strip().split('\n')[0]
                if link in dup:
                    continue
                else:
                    dup.append(link)
                try:
                    title = title.split(': ')[1]
                except:
                    pass
                #print(title)
                address= soup.findAll('span',{'class':'dsg-contact-1__address-line'})
                street = address[0].text
                city,state = address[1].text.split(', ')
                state,pcode = state.lstrip().split(' ',1)            
                coord = soup.findAll('avb-link',{'class':'dsg-contact-1__link'})[0]['data-href']
                lat,longt = coord.split('@',1)[1].split('/data',1)[0].split(',',1)
                longt = longt.split(',',1)[0]       
                phone = soup.findAll('avb-link',{'class':'dsg-contact-1__link'})[1].text.strip()        
               
                hours = soup.findAll('ul',{'class':'avb-list'})[1].text
                data.append([
                        'https://www.levinfurniture.com/',
                        link,                   
                        title,
                        street.strip(),
                        city.strip(),
                        state.strip(),
                        pcode.strip(),
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        hours.strip().replace('\r','').replace('\t','').replace('\n','').replace('PM','PM ')
                    ])
                #print(p,data[p])
                p += 1
                #input()
                
        except Exception as e :
            #print(e)
            pass

    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
