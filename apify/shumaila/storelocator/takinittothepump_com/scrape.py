import requests
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
    url = 'https://takinittothepump.com/getlocations.php'
    url1 = 'https://takinittothepump.com/location.php'
    
    r = session.get(url, headers=headers, verify=False)
    cleanr = re.compile(r'<[^>]+>')
    
    soup =BeautifulSoup(r.text, "html.parser")
    r1 = session.get(url1, headers=headers, verify=False)
    cleanr = re.compile(r'<[^>]+>')
    
    soup1 =BeautifulSoup(r1.text, "html.parser")
    divlist1 = soup1.findAll('div', {'class': 'locations'})
    #print(soup)
    divlist = soup.findAll('marker')
    for div in divlist:
       
        title = div['name']
        store = title[title.find('#')+1:len(title)]
        address= div['address']
        address= usaddress.parse(address)
        street = ""
        state = ""
        city = ""
        pcode = ""
        i = 0
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("Occupancy") != -1 or  temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        if len(street) < 2 :
            street = 'N/A'
        if len(city) < 2:
            city = 'N/A'
        if len(state) < 1:
            state = 'N/A'
        if len(pcode) < 3:
            pcode = 'N/A'
        street = street.lstrip()
        pcode = pcode.lstrip()
        city = city.lstrip()
        state = state.lstrip()
        city = city.replace(',','')
        street = street.replace(',','')
        state = state.replace(',','')
        lat = div['lat']
        longt = div['lng']
        phone = ''
        for det in divlist1:
            if det.text.find(title) > -1:
                phone = det
                break
        phone =  cleanr.sub(' ', str(phone))
        phone = phone[phone.find(':')+1:len(phone)]
        phone = phone.strip()
        print(title,phone)
        data.append(['https://takinittothepump.com/','https://takinittothepump.com/location.php', title, street, city, state, pcode, 'US', store, phone, '<MISSING>', lat, longt, '<MISSING>'])
        #print(p,data[p])
        p += 1
                

                
                
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
