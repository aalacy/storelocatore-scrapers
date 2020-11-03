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
    url = 'https://www.pizzerialimone.com/locations'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.find('section',{'class':"Main-content"}).findAll('div', {'class': "sqs-block-content"})
    titlelist = soup.find('section',{'class':"Main-content"}).findAll('h2')
   
    p = 0
    hours = ''
    for div in divlist:
        
        content = str(div).split('<h2 style=')       
        
        if len(content) > 0:
            for ct in content:
                for title in titlelist:
                    if title.text in ct:
                        ct = ct.replace('</div>','')
                        ct = '<h2 style='+ct
                        ct = BeautifulSoup(ct,'html.parser')
                        ct = re.sub(cleanr,' ',str(ct))
                        ct = re.sub(pattern,' ',str(ct)).lstrip()
                        if ct.find('HOURS') > -1:                            
                            hours = ct.replace('\n',' ').replace('HOURS','').lstrip()                            
                           
                        else:                           
                            titlenow = title.text.strip()
                            address = ct.split(titlenow,1)[1].split('(',1)[0].replace('\n',' ')
                            phone = ct.split('(',1)[1]
                            phone = '(' + phone
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
                            data.append([
                                        'https://www.pizzerialimone.com/',
                                        'https://www.pizzerialimone.com/locations',                   
                                        titlenow,
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
                                        hours
                                    ])
                           
                            p += 1
                                

        
    return data


def scrape():
    
    data = fetch_data()
    write_output(data)
  

scrape()
