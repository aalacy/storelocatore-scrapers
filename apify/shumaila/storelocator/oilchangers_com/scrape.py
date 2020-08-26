from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress
import json
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
    url = 'https://oilchangers.com/our-locations/'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split('var wpgmaps_localize_marker_data = {"1":',1)[1].split('}}};',1)[0]
    r = r +'}}'   
    while True:
        try:
            r,temp = r.split(':{',1)[1].split('},"',1)
            r = '{' + r + '}'
            loclist = json.loads(r)
            r = temp
            address = loclist['address']
            address = usaddress.parse(address)
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

            lat = loclist['lat']
            longt = loclist['lng']
            if len(state) < 2:
                state = '<MISSING>'
            if len(pcode) < 2:
                pcode ='<MISSING>'
            
            
            street  = street.lstrip()
            pcode =pcode.lstrip().replace(',','')
            state = state.lstrip().replace(',','')
            street = street.lstrip().replace(',','')
            city = city.lstrip().replace(',','')
           
            try:
                state = state.split(' ')[0]
            except:
                pass
            desc = loclist['desc']
            desc = BeautifulSoup(desc,'html.parser')
            hours = desc.find('div',{'class':'info-hours'}).text.replace('pm','pm ')
            phone = desc.findAll('a')[1].text
            title = 'Oil Changers ' + street
            if len(phone) <3 :
                phone = '<MISSING>'
            if len(hours) <3 :
                hours = '<MISSING>'
            if len (state.rstrip()) > 2 and state != '<MISSING>':
                    city = city  + ' '+ state
                    state = '<MISSING>'
            #print(phone,hours)
            data.append([
                'https://oilchangers.com',
                'https://oilchangers.com/our-locations/',                   
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
                hours.replace('\n', ' ').lstrip()
            ])
            #print(p,data[p])
            p += 1
        
            
        except Exception as e:
            print(e)
            break

        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

