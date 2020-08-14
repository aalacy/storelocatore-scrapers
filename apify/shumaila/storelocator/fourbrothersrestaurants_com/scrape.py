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
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://fourbrothersrestaurants.com/locations/'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('div', {'class': 'palm-one-whole'})
    print("states = ",len(divlist))
    for div in divlist:
        det = re.sub(cleanr,'',str(div)).lstrip().splitlines()
        title = det[0]
        street = det[1]
        city, state = det[2].split(', ')
        state,pcode = state.lstrip().split(' ',1)
        phone = det[3].lstrip()
        data.append([
                        'https://fourbrothersrestaurants.com/',
                        'https://fourbrothersrestaurants.com/locations/',                   
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
                        '<MISSING>'
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
