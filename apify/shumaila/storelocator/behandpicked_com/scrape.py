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
    
    url = 'https://behandpicked.com/store-locations'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    link_list = soup.findAll('div', {'class': 'shg-c-lg-4 shg-c-md-4 shg-c-sm-4 shg-c-xs-12'})
    
    print("link = ",len(link_list))
    p = 0
    for links in link_list:
        try:
            title = links.find('strong').text
            title = title.replace('>','').lstrip()
            links = links.find('a')
            #print(states.text.strip())
            
            link = links['href']
            #print(link)        
            r = session.get(link, headers=headers, verify=False)
            ccode = 'US'
            soup = BeautifulSoup(r.text, "html.parser")
            address = soup.find('div', {'id': 's-6ce2c10f-fdec-427c-b554-d5f32de0ceb1'}).text
            #print(address)
            phone = soup.find('div', {'id': 's-04d3662a-c533-428e-b658-f34783561e24'}).find('h4').text
            if phone.find("Phone") == -1:
                phone = soup.find('div', {'id': 's-04d3662a-c533-428e-b658-f34783561e24'})
                phone = phone.findAll('h4')
                phone = phone[1].text
            #print(phone)
            #print(title)
            phone = phone.replace('Phone:','')
            phone = phone.replace('Phone #','')
            phone = phone.lstrip()
            
            detail = str(soup)
            start = detail.find('data-latitude')
            start = detail.find('"',start)+1
            end = detail.find('"',start)
            lat = detail[start:end]
            start = detail.find('data-longitude')
            start = detail.find('"',start)+1
            end = detail.find('"',start)
            longt = detail[start:end]
            address = address.replace('Address:','')
            address = address.replace('\n','')
            address = address.lstrip()
            address = usaddress.parse(address)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
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
            city = city.lstrip()
            city = city.replace(",",'')
            street = street.replace(",",'')
            street = street.lstrip()
            state = state.lstrip()
            pcode = pcode.lstrip()

            if len(city) < 2:
                city = "<MISSING>"
            if len(street) < 2:
                street = "<MISSING>"
            if len(state) < 2:
                state = "<MISSING>"
            if len(pcode) < 2:
                pcode = "<MISSING>"
            phone = phone.replace('.','-')
            if phone.find('\n') > -1:
                phone = phone[0:phone.find('\n')]
            if len(phone) < 2:
                phone =  "<MISSING>"
            data.append([
                            'https://behandpicked.com/',
                            link,                   
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            'US',
                            "<MISSING>",
                            phone,
                            "<MISSING>",
                            lat,
                            longt,
                            "<INACCESSIBLE>"
                        ])
            #print(p,data[p])
            p += 1
        except:
            pass
      

           
            
                
                
                
             
                
           
                

                
                
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
