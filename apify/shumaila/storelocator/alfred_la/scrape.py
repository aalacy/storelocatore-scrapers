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
    
    url = 'https://alfred.la/pages/locations'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")
    maindiv = soup.find('div',{'class':'accordion-section'})    
    link_list = maindiv.findAll('a')
   # print("states = ",len(state_list))
    p = 0
    for link in link_list:
        if link['href'].find('japan') == -1 and link['href'].find('blog') > -1:
            link = 'https://alfred.la' + link['href']
            #print(link)
            r = session.get(link, headers=headers, verify=False)    
            soup =BeautifulSoup(r.text, "html.parser")
            title = soup.find('h3').text
            soup = str(soup)
            start = soup.find('[location]')
            start = soup.find(']',start)+1
            end = soup.find('[#location]',start)
            detail = soup[start:end]
            
            #detail = soup.find('div',{'class':'detail-box'}).find('li').findAll('a')
            detail = detail.lstrip().replace('\n',' ').replace('Los Angeles',' Los Angeles').replace('Pacific ',' Pacific ')
            
            #print(detail)
            address = usaddress.parse(detail)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                    "USPSBoxID") != -1:
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1

            city = city.lstrip().replace(',','')
            street = street.lstrip().replace(',','')
            state = state.lstrip().replace(',','')
            pcode = pcode.lstrip()

            start = soup.find('[opentime]')
            if start == -1:
                hours = '<MISSING>'
            else:
                start = soup.find(']',start)+1
                end = soup.find('[#opentime]',start)
                hours = soup[start:end]
            
            start = soup.find('[phone]')
            if start == -1:
                phone = '<MISSING>'
            else:
                start = soup.find(']',start)+1
                end = soup.find('[#phone]',start)
                phone = soup[start:end]

            start = soup.find('[longitude]')
            if start == -1:
                longt = '<MISSING>'
            else:
                start = soup.find(']',start)+1
                end = soup.find('[#longitude]',start)
                longt = soup[start:end]

            start = soup.find('[latitude]')
            if start == -1:
                lat = '<MISSING>'
            else:
                start = soup.find(']',start)+1
                end = soup.find('[#latitude]',start)
                lat = soup[start:end]



                
            data.append([
                        'https://alfred.la/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone.replace('\n','').replace('\xa0',''),
                        '<MISSING>',
                        lat.replace('\n','').replace('\xa0',''),
                        longt.replace('\n','').replace('\xa0',''),
                        hours.replace('\n',' ').replace('\xa0','').replace('&amp;','&').lstrip().rstrip()
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
