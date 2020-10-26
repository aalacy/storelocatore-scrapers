from bs4 import BeautifulSoup
import csv
import json
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
    url = 'https://parknationalbank.com/about/locations/'
    flag = True
    while flag:
        print(url)
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        r = r.text.split('var markers =',1)[1].split('}]')[0]
        r = r + '}]'
        loclist = json.loads(r)       
        
        divlist = soup.findAll('div',{'class':'location-list-result'})
       
        for div in divlist:
            title = div.find('h4').text.replace('\n','').lstrip()
            link = div.find('h4').find('a')['href']
            phonelinks = div.findAll('a')
            phone  = '<MISSING>'
            lat  = '<MISSING>'
            longt  = '<MISSING>'
            
            address= str(div.find('span',{'class':'branch-address'}).text)
            
            #input()
            address = re.sub(pattern," ",address).lstrip()
            phone = address.split(' ')[-1].replace('\n','')
            
            
            if phone.find('-') == -1:
                phone ='<MISSING>'

            else:
                address = address.replace(phone,'')
            print(address)
            try:
                street,city,state = address.split(', ')
            except:
                street,temp,city,state = address.split(', ')
                street = street +' '+ temp
                
            state,pcode= state.lstrip().split(' ',1)
            pcode =pcode.replace('\n','')
            try:
                hours = div.find('div', {'class': 'col-3-flex'}).text.replace('\n', ' ').split(' Lobby Hours  ')[1]
            except:
                hours = "<MISSING>"
            stored = div.find('div', {'class': 'links'})
            stored= str(stored)            
            store = stored.split('data-locationID="')[1].split('"')[0]
            for loc in loclist:
                if loc["title"] == title:
                    lat = loc['lat']
                    longt = loc['lng']
                    break
            ltype = ''
            try:
                ltype = div.find('li',{'class':'feature-branch'}).text + ' '
            except:
                pass
            try:
                ltype = ltype + '| '+ div.find('li',{'class':'feature-atm'}).text 
            except:
                pass
            if ltype == '':
                ltype = '<MISSING>'
            data.append([
                'https://parknationalbank.com',
                link,
                title,
                street,
                city,
                state,
                pcode,
                'US',
                store,
                phone,
                ltype,
                lat,
                longt,
                hours
            ])
            print(p,data[p])
            p += 1
            #input()

        next = soup.find('a', {'class': 'next page-numbers'})
        try:

            url = next['href']

        except:
            flag = False

    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()

