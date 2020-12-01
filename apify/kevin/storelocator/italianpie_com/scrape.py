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
    url = 'http://italianpie.com/italianpie-locations.htm'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('p')
   # print("states = ",len(state_list))
    p = 0
    for div in divlist:
        try:
            title = div.find('strong').text.replace('\n','')
            content = re.sub(pattern,'\n',div.text).splitlines()           
            street = content[1]
            phone = content[2]
            hours = ' '.join(content[3:])
            if 'DOWNTOWN' in title or 'HARAHAN' in title or 'KENNER' in title:
                city = "New Orleans"
            else:
                city = title
            state = 'LA'           
            pcode = '<MISSING>'
            if len(hours) < 3 and title == 'The Original Italian Pie':
                
                city = 'New Orlean'
                pcode = phone.split('. ')[-1]
                phone = '<MISSING>'
                hours = '<MISSING>'
            data.append([
                        'http://italianpie.com/',
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
                        '<MISSING>',
                        '<MISSING>',
                        hours
                    ])
            #print(p,data[p])
            p += 1
                
        except:
            continue
        
  
    return data


def scrape():
   
    data = fetch_data()
    write_output(data)
  

scrape()
