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
    url = 'https://www.janddmarket.com/'
    r = session.get(url, headers=headers, verify=False)
    
    soup =BeautifulSoup(r.text, "html.parser")
    links = []
    linklist = soup.select("a[href*=location]")
   # print("states = ",len(state_list))
    p = 0
    for link in linklist:
        if link['href'] in links or link['href'].find('#') > -1:
            continue

        links.append(link['href'])
        title = link.text.replace('\n','')
        link = 'https://www.janddmarket.com'+link['href']        
        r = session.get(link, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        street = soup.find('span',{'itemprop':'streetAddress'}).text
        city = soup.find('span',{'itemprop':'addressLocality'}).text
        state = soup.find('span',{'itemprop':'addressRegion'}).text
        pcode = soup.find('span',{'itemprop':'postalCode'}).text
        phone = soup.find('span',{'itemprop':'telephone'}).text
        hourlist = soup.findAll('div',{'class':'open-hours-item'})
        hours = ''
        for hr in hourlist:
            hours = hours + hr.text.lstrip().replace('\n','') + ' '
        #print(hours)
        lat,longt = soup.find('a',{'class':'dmMap'})['href'].split('sll=',1)[1].split(',',1)
        
        data.append([
                        'https://www.janddmarket.com/',
                        link,                   
                        title,
                        street,
                        city.replace(',',''),
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
