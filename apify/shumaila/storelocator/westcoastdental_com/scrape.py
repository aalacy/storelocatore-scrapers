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
    p = 0
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://westcoastdental.com/locations/locations.json'
    loclist = session.get(url, headers=headers, verify=False).json()['serviceAreas']['serviceArea']
      
    for loc in loclist:
        store = loc['_clientId']
        title = loc['_name']
        street = loc['_address']
        city = loc['_city']
        state = loc['_state']
        pcode = loc['_zip']
        phone = loc['_phone']        
        
        lat = loc['_lat']
        longt = loc['_lng']
        link = loc['_url']
        #print(link)
        if link.find('http') == -1:
            link = 'https://westcoastdental.com'+link        
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text,'html.parser')
            hours = soup.find('div',{'id':'hours'}).text
            hours = re.sub(pattern,' ',hours).replace('\n',' ')
            hours = hours.replace('Office Hours','').lstrip()
        else:
            hours = '<MISSING>'

        
        data.append([
                        'https://westcoastdental.com',
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
