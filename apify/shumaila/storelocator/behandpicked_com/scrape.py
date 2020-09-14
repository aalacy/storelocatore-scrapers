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
    pattern = re.compile(r'\s\s+') 
    url = 'https://behandpicked.com/handpicked-stores/'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.find('div',{'class':'body'}).find('div',{'class':'container'})
    titlelist = soup.find('div',{'class':'body'}).find('div',{'class':'container'}).findAll('strong')
    content = re.sub(cleanr,' ',str(divlist))
    content =re.sub(cleanr,'\n',str(content))
    for i in range(1,len(titlelist)):
        det,content = content.split(titlelist[i].text,1)
        if i == 1:
            det = det.split(titlelist[0].text,1)[1]
        det = det.lstrip()
        if i == (len(titlelist)-1):
            det = content
        #print(det)
        if det.find('location is closed') > -1:
            continue
        title = titlelist[i-1].text
        address = det.split('Phone')[0]
        phone = det.split('Phone')[1].split('E-mail')[0]
        try:
            hours = det.split('Hours')[1].split('Th')[0]
        except:
            hours = det.split('Hours')[1].split('E-mail')[0]
            phone = det.split('Phone')[1].split('\n')[-1]
            
        lat = '<MISSING>'
        longt = '<MISSING>'
        store = '<MISSING>'
        ltype = '<MISSING>'
        try:
            address = address.split('\n',1)[0].lstrip()
        except:
            pass
        try:
            phone = phone.split('\n',1)[0].lstrip()
        except:
            pass
        try:
            hours = hours.split('\n',1)[0].lstrip()
        except:
            pass
        try:
            hours = hours.split('Locate',1)[0].lstrip()
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
        
        #print(det)        
        data.append([
                        'https://behandpicked.com/',
                        'https://behandpicked.com/handpicked-stores/',                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone.replace(': ',''),
                        ltype,
                        lat,
                        longt,
                        hours.replace(': ','').replace('&amp;','-'),
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
