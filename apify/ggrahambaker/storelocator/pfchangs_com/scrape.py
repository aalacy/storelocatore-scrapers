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
    titlelist = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.pfchangs.com/locations/us.html'
    r = session.get(url, headers=headers, verify=False)
    p = 0
    soup =BeautifulSoup(r.text, "html.parser")
    statelist = soup.findAll('a',{'class':'Directory-listLink'})
    for slink in statelist:
        slink = 'https://www.pfchangs.com/locations/'+slink['href']        
        r = session.get(slink, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        citylist = soup.findAll('a',{'class':'Directory-listLink'})
        for clink in citylist:
            clink = clink['href'].replace('../','https://www.pfchangs.com/locations/')
           
            r = session.get(clink, headers=headers, verify=False)
            soup =BeautifulSoup(r.text, "html.parser")
            linklist = soup.findAll('a',{'class':'Teaser-titleLink'})
            flag = 0
            if len(linklist) == 0:
                linklist.append(clink)
                flag = 1
            for link in linklist:                
                if flag == 0:
                    #print(link['href'])
                    link = link['href'].replace('../../../../','https://www.pfchangs.com/locations/')
                    link = link.replace('../../','https://www.pfchangs.com/locations/')
                    if link in titlelist:
                        continue
                    r = session.get(link, headers=headers, verify=False)
                    soup =BeautifulSoup(r.text, "html.parser")
                    
               
                title = soup.find('h1').find('span',{'class':'LocationName'}).text
                street = soup.find('meta',{'itemprop':'streetAddress'})['content']
                city = soup.find('meta',{'itemprop':'addressLocality'})['content']
                lat = soup.find('meta',{'itemprop':'latitude'})['content']
                longt = soup.find('meta',{'itemprop':'longitude'})['content']
                pcode = soup.find('span',{'itemprop':'postalCode'}).text
                state = soup.find('abbr',{'itemprop':'addressRegion'}).text
                phone = soup.find('div',{'itemprop':'telephone'}).text
                store = link.split('/')[-1].split('-',1)[0]
                hours = soup.find('table',{'class':'c-hours-details'}).text
                hours = hours.replace('PM','PM ').replace(street,'')
                hours = hours.replace('Day of the WeekHours','')
                hours = hours.replace('11',' 11')
                hours = hours.replace('Closed',' Closed ')
                store = store.replace('.html','')
                if link in titlelist or 'Closed' in title:
                    continue
                titlelist.append(link)
                data.append([
                        'https://www.pfchangs.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
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
