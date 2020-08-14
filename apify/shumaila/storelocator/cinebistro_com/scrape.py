from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
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
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://www.cmxcinemas.com/theaters/'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split(' var cinemas =')[1].split(']}];')[0]
    r = r + ']}]'
    loclist = json.loads(r)
    for loc in loclist:
        #print(loc)
        
        title = loc['name']
        store = loc['id']
        lat = loc['lat']
        longt = loc['lng']
        address1 = loc['info']['address']
        phone =loc['info']['phone']
        hours =loc['info']['hours']
        address = usaddress.parse(address1)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find('Occupancy') != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
            
        state = state.lstrip().replace(',','')
        street  = street.lstrip().replace(',','')
        pcode = pcode.lstrip().replace(',','')
        city = city.lstrip().replace(',','')
         
        if state == '':
            street,city = address1.split(', ')
            state = loc['state']['short_name']
            pcode = '<MISSING>'
        #print(street,city, state,pcode)
        #print(phone)
        try:
            phone = phone.replace('+1 ','') 
        except:
            
            phone = '<MISSING>'
            
        data.append([
                        'https://www.cmxcinemas.com',
                        'https://www.cmxcinemas.com/theaters/',                   
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
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

