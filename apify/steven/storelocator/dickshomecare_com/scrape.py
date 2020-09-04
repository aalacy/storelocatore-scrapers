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
    url = 'https://dickshomecare.com/contact/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.findAll('section', {'class': 'elementor-element'})
    #print(len(divlist))
    for div in divlist:
        if div.find('h2'):
            title = div.find('h2').text
            det = div.findAll('p')
            address = det[0]
            address = re.sub(cleanr,' ',str(address)).lstrip()
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
            pcode = pcode.lstrip().replace(',','')
            state = state.lstrip().replace(',','')    
            city = city.lstrip().replace(',','') 
            phone =det[1].text
            hours =det[2].text
            try:
                phone = phone.split('Fax',1)[0].replace('Phone:','')
            except:
                pass
            hours = hours.replace('Hours:','').replace('M-F','M-F ')
            coord = div.findAll('iframe')[1]['src'].split('!2d',1)[1].split('!2m',1)[0]           
            lat,longt =coord.split('!3d',1)
            if city.find('East') > -1:
                street = street + ' East'
                city= city.replace('East ','')
            data.append([
                        'https://dickshomecare.com/',
                        'https://dickshomecare.com/contact/',                   
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
                
            
 
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
