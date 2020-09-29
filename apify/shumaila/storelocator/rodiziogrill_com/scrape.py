from bs4 import BeautifulSoup
import csv
import string
import re, time,json

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
    url = 'https://www.rodiziogrill.com/locations.aspx'
    r = session.get(url, headers=headers, verify=False)
    
    soup =BeautifulSoup(r.text, "html.parser")
   
    loclist = soup.find('div',{'class':'locationsList'}).findAll('a')
   # print("states = ",len(state_list))
    p = 0
    for loc in loclist:
        if loc.text.lower().find('soon') == -1:
            link = loc['href']
            #print(link)
            r = session.get(link, headers=headers, verify=False)
            det = r.text.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0]
            det = re.sub(pattern,'',str(det))
            det = json.loads(det)
            #print(det)
            street = det['address']['streetAddress']
            state = det['address']["addressRegion"]
            city = det['address']["addressLocality"]
            pcode =  det['address']["postalCode"]
            try:
                phone = det['telephone']
            except:
                phone = '<MISSING>'
            title = det['name']
            lat,longt = r.text.split('LatLng(',1)[1].split(')',1)[0].split(',')
            soup = BeautifulSoup(r.text,'html.parser')
            hours = soup.find('div',{'class':'Column2'}).text.replace('\n',' ').lstrip().replace('Hours ','')
            #print(hours)
            try:
                hours = hours.split('*',1)[0]
            except:
                pass
            try:
                hours = hours.split('!',1)[1]
            except:
                pass
            try:
                hours = hours.split('Special',1)[0]
            except:
                pass
            if state.strip() == 'Wisconsin':
                state = 'WI'
            data.append([
                        'https://www.rodiziogrill.com/',
                        link,                   
                        title,
                        street.replace('\u200e',''),
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        hours.replace('\r','').strip().replace('day','day ').replace('  ',' ')
                    ])
            #print(p,data[p])
            p += 1

            #input()
       
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
