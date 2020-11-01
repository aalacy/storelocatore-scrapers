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
    url = 'https://salonsbyjc.com/our-locations/'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('div', {'class': "place"})
    coordlist = soup.findAll('div', {'class': "marker"}) 
    p = 0
    for div in divlist:
        try:
            title = div.find('h3').text
            try:
                title = title +' '+div.find('h4').text
            except:
                pass
            link = div.find('a')['href']
            
            address= div.find('p',{'class':'location_gaddress'}).text.replace(',USA','')
            if address.find('USA') > -1:
                ccode = 'US'
            elif address.find('Canada') > -1:
                ccode = 'CA'
            phone= div.find('span',{'class':'contact_number'}).text
            
            
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
            state = state.lstrip().replace(',','').replace('USA','')
            pcode = pcode.lstrip().replace(',','')
            ccode = 'US'

            
            if len(pcode) < 3:
                pcode = '<MISSING>'
            if len(phone.strip()) < 3:
                phone = '<MISSING>'
            if state == '' and street.find('Canada')> -1:
                street = street.replace('Canada','')               
                pcode = ' '.join(street.rstrip().split(' ')[-2:])
                state = street.rstrip().split(' ')[-3]
                city = street.rstrip().split(' ')[-4]
                street = street.split(city,1)[0]
                ccode = 'CA'
            try:
                phone = phone.lstrip().split('(Se',1)[0]
            except:
                pass
            lat = longt='<INACCESSIBLE>'
            
            for coord in coordlist:                
                if street.lstrip().split(' ',1)[0] in coord.text.strip() and city in coord.text.strip():
                    
                    lat = coord['data-lat']
                    longt = coord['data-lng']                    
                    break
                   
            data.append([
                        'https://salonsbyjc.com',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        ccode,
                        '<MISSING>',
                        phone.replace('\u202a','').replace('\u202c',''),
                        '<MISSING>',
                        lat,
                        longt,
                        '<MISSING>'
                    ])
            #print(p,data[p])
            p += 1
                
            
            
        except Exception as e:
            #print(e)
            pass
        
           
        
    return data


def scrape():
   
    data = fetch_data()
    write_output(data)

scrape()
