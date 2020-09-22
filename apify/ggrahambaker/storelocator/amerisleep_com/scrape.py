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
    url = 'https://amerisleep.com/retail/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('span', {'class': "bold"})
    print("states = ",len(divlist))
    p = 0
    for div in divlist:
      
        link = div.find('a')['href']
        #print(link)
        r = session.get(link, headers=headers, verify=False)
        loc = r.text.split('<script type="application/ld+json">',1)[1].split('"image":',1)[0]
        loc = re.sub(pattern,'',loc).replace('\n','').split(',"sameAs"',1)[0]
        loc = loc + '}'
        #print(loc)
        loc = json.loads(loc)
        longt,lat = r.text.split('id="map-canvas"><iframe',1)[1].split('!2d',1)[1].split('!2m',1)[0].split('!3d',1)
        street = loc['address']['streetAddress']
        city =  loc['address']['addressLocality']
        state =  loc['address']['addressRegion']
        pcode =  loc['address']['postalCode']
        phone = loc['telephone'].replace('+1-','')        
        title = loc['name']
        if len(lat) > 20:
            lat = loc['geo']['latitude']
            longt = loc['geo']['longitude']
        hours=  BeautifulSoup(r.text,'html.parser').find('div',{'class':'store-hours'}).text
        hours = re.sub(pattern,' ',hours) .replace('\n',' ') .lstrip()
        if len(phone) < 12:
            phone = phone +'0'
        
        data.append([
                    'https://amerisleep.com',
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
