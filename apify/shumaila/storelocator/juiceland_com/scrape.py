from bs4 import BeautifulSoup
import csv
import string,json
import re, time, usaddress

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
    p = 0
    url = 'https://www.juiceland.com/all-locations/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
    linklist = soup.find('main').findAll('h4')
    for link in linklist:
        title = link.text
        link = link.find('a')['href']
        #print(link)
        r = session.get(link, headers=headers, verify=False)  
        soup =BeautifulSoup(r.text, "html.parser")
        loc = str(soup).split('"locations":[',1)[1].split(']};',1)[0]
        loc = json.loads(loc)
        street = loc['address']
        city = loc['city']
        state = loc['state']
        pcode = loc['zip']
        lat = loc['lat']
        longt = loc['lng']
        store = loc['id']
        hours = soup.find('div',{'class':'single-wpsl__right-hours'}).text.replace('\nStore Hours:\n','').replace('\n',' ').replace('\r','').strip()
        try:
            hours = hours.split('Shop')[0]
        except:
            pass
        phone = soup.find('span',{'class':'phone'}).text
        data.append([
                        'https://www.juiceland.com/',
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
        #input()
        p += 1
           
    
            
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
