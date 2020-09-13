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
    p = 0
    pattern = re.compile(r'\s\s+') 
    url = 'https://www.firstchoicedental.com/locations//json?unit=m'
    loclist = session.get(url, headers=headers, verify=False).json()['locations']
    for loc in loclist:
        store = loc['ID']
        title = loc['Title']
        try:
            phone = loc['Phone']
        except:
            phone = '<MISSING>'
        street = loc['Address']
        city  = loc['City']
        state = loc['State']
        pcode = loc['PostalCode']
        lat = loc['Lat']
        longt = loc['Lng']
        link = 'https://www.firstchoicedental.com' + loc['LocLink']
        r = session.get(link, headers=headers, verify=False)
        r = BeautifulSoup(r.text,'html.parser')
        try:
            hours = r.text.split('Hours')[1].split('Service')[0].replace('\n','').strip()
            hours = re.sub(pattern, '',hours).replace('PM','PM ')
        except:
            hours = '<MISSING>'
        data.append([
                        'https://www.firstchoicedental.com/',
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
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
