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
    
    url = 'https://wildwillysburgers.com/#locations'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    div_list = soup.findAll('div', {'class': 'location-item'})
   # print("states = ",len(state_list))
    p = 0
    for div in div_list:
        title = div.find('p').text
        link = 'https://wildwillysburgers.com'+ div.find('a')['href']
        r = session.get(link, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        mainul = soup.find('ul',{'class':'l-c-box__list'})
        try:
            phone = mainul.find('a',{'class':'tel'}).text
        except:
            phone = '<MISSING>'
        try:
            address = mainul.find('address').text
            address = usaddress.parse(address)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
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
            if len(street) < 2:
                street =  '<MISSING>'
            if len(city) < 2:
                city =  '<MISSING>'
            if len(state) < 2:
                state =  '<MISSING>'
            if len(pcode) < 2:
                pcode =  '<MISSING>'
        except Exception as e:
            print(e)
            street =  '<MISSING>'
            city =  '<MISSING>'
            state =  '<MISSING>'
            pcode =  '<MISSING>'
        
        try:
            hours = soup.find('div',{'class':'h-wrap'}).find('p').text.replace('We are open ','').replace(' for take out and curbside service.','')
            if hours == "We're Excited To See You":
                hours = '<MISSING>'
        except:
            hours = '<MISSING>'
        
        
        soup = str(soup)
        start = soup.find('"lat"')
        if start == -1:
            lat = '<MISSING>'
        else:
            start = soup.find(':',start)
            start = soup.find('"',start)+1
            end = soup.find('"',start)
            lat = soup[start:end]
    
        start = soup.find('"lng"')
        if start == -1:
            longt = '<MISSING>'
        else:
            start = soup.find(':',start)
            start = soup.find('"',start)+1
            end = soup.find('"',start)
            longt = soup[start:end]

        
        data.append([
                    'https://wildwillysburgers.com/',
                    link,                   
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
