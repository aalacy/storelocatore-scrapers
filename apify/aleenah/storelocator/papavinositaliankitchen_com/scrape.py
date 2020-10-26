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
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.papavinositaliankitchen.com/locations.html'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.findAll('td', {'class': "wsite-multicol-col"})
   # print("states = ",len(state_list))
    p = 0
    for div in divlist:
        try:
            title = div.find('h2').text
            #print(title)
            content = div.find('div',{'class':'paragraph'})
            content = re.sub(cleanr,'\n',str(content))
            content = re.sub(pattern,'\n',content).lstrip().splitlines()
            phone = content[1]
            street = content[2]
            city,state = content[3].split(', ')
            state,pcode = state.lstrip().split(' ',1)
            hours = ' '.join(content[4:])
            hours = hours.replace('\u200b','')            
            longt = div.find('iframe')['src'].split('long=',1)[1].split('&',1)[0]
            lat = div.find('iframe')['src'].split('lat=',1)[1].split('&',1)[0]
            data.append([
                        'https://www.papavinositaliankitchen.com/',
                        url,                   
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
            
        except Exception as e:
            #print(e)
            pass
                
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
