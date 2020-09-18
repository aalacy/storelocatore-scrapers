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
    p = 0
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.mariaempanada.com/find-us'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('div', {'class': "sqs-block html-block sqs-block-html"})
    print("states = ",len(divlist))
    #input()
    for div in divlist:
        try:
           
            title = div.find('strong').text
            #print(title)
            if div.text.find('TEMPORARILY CLOSED') > -1:
                title = title + '( TEMPORARILY CLOSED )'
            if title.find('@mariaempanada') > -1:
                continue
            
            det = div.findAll('p')
            
            address = det[1]
            address =re.sub(cleanr,' ',str(address)).rstrip()
            address = re.sub(pattern,' ',address)
            phone = address.split(' ')[-1]
            if len(phone) < 8:
                phone = '<MISSING>'
            else:
                address = address.replace(phone,'')
            
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
            hours = det[3].text.replace('AM',' AM ').replace('PM',' PM ')
            data.append([
                        'https://www.mariaempanada.com/',
                        'https://www.mariaempanada.com/find-us',                   
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
                        hours.replace('\xa0','')
                    ])
            #print(p,data[p])
            p += 1
                
            
            
            
        except Exception as e:
            
            pass
    
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
