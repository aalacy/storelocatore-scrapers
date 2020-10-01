from bs4 import BeautifulSoup
import csv
import string
import re, time,json,usaddress

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
            
            lat,longt = r.text.split('LatLng(',1)[1].split(')',1)[0].split(',')
            soup = BeautifulSoup(r.text,'html.parser')
            title = soup.find('title').text.split(' |')[0]
            try:
                phone = soup.find('div',{'class':'locationPhone'}).find('a').text
            except:
                phone = '<MISSING>'
            address = soup.find('div',{'class':'Column4'}).findAll('div')[1].text.replace('\n',' ')
            #print(address)
            if address.find('Located inside') > -1 or address.find('between') > -1:
                #print('1')
                address  = soup.find('div',{'class':'Column4'}).findAll('div')[2].text.replace('\n',' ')
            try:
                if len(address.rstrip().split(' ')[-1]) == 5:
                    pass
                else:
                    address= address + ' '+soup.find('div',{'class':'Column4'}).find('p').text
                    #print('yes')
            except:
                pass
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

            street = street.lstrip().replace(',','')
            city = city.lstrip().replace(',','')
            state = state.lstrip().replace(',','')
            pcode = pcode.lstrip().replace(',','')
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
                        longt.strip(),
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
