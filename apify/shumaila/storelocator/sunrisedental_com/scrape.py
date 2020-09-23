from bs4 import BeautifulSoup
import csv
import string
import re, time
import json,usaddress
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
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://sunrisedental.com/wp-json/wp/v2/pages/1121'
    p = 0
    r = session.get(url, headers=headers, verify=False).json()['content']['rendered']
    soup = BeautifulSoup(r,'html.parser')
    divlist = soup.findAll('div',{'class':'swiper-slide-contents'}) 
    for div in divlist:
        #print(div.text)
        title = div.text.split('Phone')[0]
        phone = div.text.split(': ',1)[1].split('\n',1)[0]
        address = div.text.split('Address: ',1)[1].split('More',1)[0]
        address = usaddress.parse(address.replace('United States',''))
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

        street = street.lstrip().replace(',','')
        city = city.lstrip().replace(',','')
        state = state.lstrip().replace(',','')
        pcode = pcode.lstrip().replace(',','')
        if len(pcode) < 3:
            pcode = '<MISSING>'
        if len(state.strip()) > 2:
            state,pcode = state.split(' ',1)
        try:
            pcode = pcode.split('Click')[0]
        except:
            pass
        try:
            city = city.split('Click')[0]
        except:
            pass
        try:
            phone = phone.split('Address',1)[0]
        except:
            pass
        data.append([
                'https://sunrisedental.com/',
                'https://sunrisedental.com/contact-us_new/',                   
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

