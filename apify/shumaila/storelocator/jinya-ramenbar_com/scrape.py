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
    
    url = 'http://jinya-ramenbar.com/locations/'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    repo_list = soup.findAll('script', {'type': 'text/javascript'})
    
    print("link = ",len(repo_list))
    p = 0
    detail = str(repo_list[1].text)
    start = 0
    while True:
        start = detail.find('"url"',start)
        if start > -1:
            start = detail.find(":",start) + 2
            end = detail.find(",",start)-1
            link = detail[start:end]
            link =  link.replace('\\','')
            link = "http://jinya-ramenbar.com"+link              
            start = end
            start = detail.find('"shopname"',start)
            start = detail.find(":",start) + 2
            end = detail.find(",",start)-1
            title = detail[start:end]                         
            start = end
            #print(title)
            if title.lower().find('coming soon') == -1:
                start = detail.find('"lat"',start)
                start = detail.find(":",start) +1 
                end = detail.find(",",start)
                lat = str(detail[start:end])                
                start = end
                if lat == 'null':
                    lat = "<MISSING>"
                start = detail.find('"lng"',start)
                start = detail.find(":",start) +1 
                end = detail.find(",",start)
                longt = str(detail[start:end])                
                start = end
                if longt == 'null':
                    longt = "<MISSING>"
                start = detail.find('"address"',start)
                start = detail.find(":",start) + 2
                end = detail.find("tel",start)-2
                address= detail[start:end-1]
                address = address.replace('\n','')
                address = address.lstrip()
                #print(address)
                street = ""
                city = ""
                state = ""
                pcode = ""
                ccode =''
                if address.lower().find('canada') == -1:
                    address = usaddress.parse(address)
                    i = 0
                    ccode = 'US'
                    while i < len(address):
                        temp = address[i]
                        if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                                temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                            "USPSBoxID") != -1:
                            street = street + " " + temp[0]
                        if temp[1].find("PlaceName") != -1:
                            city = city + " " + temp[0]
                        if temp[1].find("StateName") != -1:
                            state = state + " " + temp[0]
                        if temp[1].find("ZipCode") != -1:
                            pcode = pcode + " " + temp[0]
                        i += 1
                else:
                    mstart = 0
                    mend = address.find(',',mstart)
                    street = address[mstart:mend]
                    mstart = mend + 1
                    if street.find('Vancouver') == -1:
                        mend = address.find(',',mstart)
                        city = address[mstart:mend]
                        mstart = mend + 1
                    else:
                        street = street.replace('Vancouver','')
                        city = 'Vancouver'
                    address = address[mstart:address.find('Canada')].lstrip()
                    if address.lower().find('british columbia') == -1:
                        state = address[0:address.find(' ')]
                        pcode = address[address.find(' ')+1:len(address)-1]
                    else:
                        state = 'BC'
                        address = address.replace('British Columbia','')
                        pcode = address.lstrip()
                    ccode = 'CA'
                    
                    
                city = city.lstrip()
                city = city.replace(",",'')
                street = street.replace(",",'')
                street = street.lstrip()
                state = state.lstrip()
                pcode = pcode.lstrip()
                if state == 'Washington':
                    state = 'WA'

                if len(city) < 2:
                    city = "<MISSING>"
                if len(street) < 2:
                    street = "<MISSING>"
                if len(state) < 2:
                    state = "<MISSING>"
                if len(pcode) < 2:
                    pcode = "<MISSING>"
                start = end                
                start = detail.find('"tel"',start)
                start = detail.find(":",start) + 2
                end = detail.find(",",start)-1
                phone= detail[start:end]
                if phone.find('\\') > -1:
                    phone = phone[0:phone.find('\\')]
                if len(phone) < 2:
                    phone  = "<MISSING>"
                start = end
                start = detail.find('"hours"',start)
                start = detail.find(":",start) + 2
                end = detail.find(",",start)-1
                hours= detail[start:end]
                hours = hours.replace('\\r','')
                hours = hours.replace('\\n',' ')
                hours = hours.replace('<br \\/> ',' ')
                hours = hours.replace('am',' am')
                hours = hours.replace('pm',' pm')
                hours = hours.replace('\\','')
                if hours.find('2019') > -1:
                    hours = hours[0:hours.find('2019')]
                    hours = hours.rstrip()
                start = end
                if len(phone) < 2:
                    phone= "<MISSING>"
                if len(hours) < 2:
                    hours = "<MISSING>"
                state = state.replace(',','')
                pcode = pcode.replace(',','')
                city = city.replace(',','')
                data.append([
                            'http://jinya-ramenbar.com/',
                            link,                   
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            ccode,
                            "<MISSING>",
                            phone,
                            "<MISSING>",
                            lat,
                            longt,
                            hours])
                #print(p,data[p])
                p += 1
                
                
        else:
            break
        
                
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
