from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress

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
    url = 'https://mtmtavern.com/locations-menus/'
    r = session.get(url, headers=headers, verify=False) 
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.find('div',{'id':'LocationsList'}).findAll('div',{'class':'location-detail'})
    print("states = ",len(divlist))
    p = 0
    for div in divlist:
        try:
            link = div.find('div',{'class':'h3'}).find('a')['href']
            #print(link)
            title = div.find('div',{'class':'h3'}).find('a').text            
            address = div.find('div',{'class':'location-address'}).find('p').text.replace('\n','')
            phone = div.find('div',{'class':'location-address'}).find('a').text
                       
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
            r = session.get(link, headers=headers, verify=False)
            try:
                soup =BeautifulSoup(r.text, "html.parser")
                hours = soup.find('div',{'id':'BusinessHours'})
                hours = re.sub(cleanr,' ',str(hours))
                hours = re.sub(pattern,' ',hours)
            except:
                hours = '<MISSING>'
            if hours == 'None':
                hours = '<MISSING>'
            if city == '':
                city,state = state.split(' ',1)
            data.append([
                        'https://mtmtavern.com/',
                        link,                   
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
                        hours.replace('\n','')
                    ])
            #print(p,data[p])
            p += 1
                
            
            
        except Exception as e:
            print(e)
            pass
        
           
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
