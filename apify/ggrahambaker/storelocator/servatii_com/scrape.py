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
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.servatii.com/locations'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")   

    titlelist = soup.findAll('h2')
    divlist = soup.findAll('div')
   # print("states = ",len(state_list))
    p = 0
    content = ''
    for div in divlist:
        try:
            for title in titlelist:                
                if div.text.find(title.text) > -1:                    
                    content = div.text
                                     
                    break
            break   
        except Exception as e:
            print(e)
            pass

    for title in titlelist:
        det = content.split(title.text)[1].split('HOURS OF OPERATION')[0]
        title = title.text.replace('HOURS OF OPERATION','')
        address = det.split('Mon -',1)[0]
        if address.find('COMING SOON') > -1:
            continue
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
        hours=  'Mon -' + det.split('Mon -',1)[1].split('Get')[0]
        data.append([
                        'https://www.servatii.com/',
                        'https://www.servatii.com/locations',                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        hours.replace('pm','pm ')
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
