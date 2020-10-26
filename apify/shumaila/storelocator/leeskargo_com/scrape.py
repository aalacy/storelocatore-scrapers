import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
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
    pattern = re.compile(r'\s\s+')
    url = 'http://leeskargo.com/find-us.html'
        
    r = session.get(url, headers=headers, verify=False)
    
    
    soup =BeautifulSoup(r.text, "html.parser")  
    divlist = soup.findAll('tr', {'class': 'wsite-multicol-tr'})
    print(len(divlist))
    #print(soup)
    
    for div in divlist:
        if div.find('iframe'):
            det = div.find('div',{'class':'paragraph'})            
            det = re.sub(pattern, " ", str(det)).strip()
            det = cleanr.sub('\n', str(det)).strip()
            #det = det.replace('\n\n',' ')
            det = det.replace('\u200b','')
            det = det.splitlines()
            while("" in det) : 
                det.remove("") 
            street = det[0]
            city,state= det[1].split(', ')
            try:
                state,pcode = state.lstrip().split(' ')
            except:
                pcode = '<MISSING>'
            phone = det[2]
            hours = ''
            for d in range(3,len(det)):
                hours = hours + det[d] +' '
            coord = div.find('iframe')['src']
            start = coord.find('long=')
            start = coord.find('=',start)+1
            end = coord.find('&',start)
            longt = coord[start:end]
            start = coord.find('lat=')
            start = coord.find('=',start)+1
            end = coord.find('&',start)
            lat = coord[start:end]
            #print(street,city,state,pcode,hours,lat,longt)
            data.append(['http://leeskargo.com/','http://leeskargo.com/find-us.html', '<MISSING>', street, city, state, pcode, 'US', '<MISSING>', phone, '<MISSING>', lat, longt, hours])
            print(p,data[p])
            p += 1
            
        else:
            pass
        
                

                
                
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
