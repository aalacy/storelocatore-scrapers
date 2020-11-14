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
    # Your scraper here
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.lowes.com/content/lowes/desktop/en_us/stores.xml'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")   
    linklist = soup.findAll('loc')
    titlelist = []
    p = 0
    for link in linklist:
        link = link.text
        r = session.get(link, headers=headers, verify=False)
        try:
            hourlist,r = r.text.split('<script type="application/ld+json">',1)[1].split('</script',1)
            address,r = r.split('<script type="application/ld+json">',1)[1].split('</script',1)
            lat = r.split('"lat":"',1)[1].split('"',1)[0]
            longt = r.split('"long":"',1)[1].split('"',1)[0]
           
            hourlist = json.loads(hourlist)
            address = json.loads(address)        
            street = address['streetAddress']
            city = address['addressLocality']
            state = address['addressRegion']
            pcode = address['postalCode']
            phone = address['telephone']
            title = hourlist['name']
            hourlist = hourlist['openingHours']
            hours = ' '.join(hourlist)
            store = link.split('/')[-1]
            ccode = 'US'
            
           
                    
        except:
            soup = BeautifulSoup(r.text,'html.parser')
            hours = soup.find('div',{'aria-labelledby':"storeHoursSection"}).text
            r = session.get('https://www.lowes.ca/apim/stores/2922OL', headers=headers, verify=False).json()
            pcode = r['zip']
            ccode = 'CA'
            street = r['address']
            state= 'ON'
            city = r['city']
            title = r["store_name"]
            store = r['id']
            phone = r['phone']
        
              
    
        if street in titlelist:
            continue
        titlelist.append(street)
        data.append(['https://www.lowes.com/',
                            link,                   
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            ccode,
                            store,
                            phone,
                            '<MISSING>',
                            lat,
                            longt,
                            hours
                        ])
        
        p += 1
           
        
    return data


def scrape():
    
    data = fetch_data()
    write_output(data)
   

scrape()
