import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time

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
    
    url = 'https://www.bankwithunited.com/contact-us#location'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    title_list = soup.findAll('div', {'class': 'views-field-field-branch-name'})
    street_list = soup.findAll('div', {'class': 'views-field-field-address-address-line1'})
    city_list = soup.findAll('span', {'class': 'views-field-field-address-locality'})
    state_list = soup.findAll('span', {'class': 'views-field-field-address-administrative-area'})
    pcode_list = soup.findAll('span', {'class': 'views-field-field-address-postal-code'})
    phone_list = soup.findAll('div', {'class': 'views-field-field-phone-number'})
    coords_list = soup.findAll('span', {'property': 'geo'})
    
    
    print("title = ",len(title_list))
    print("city = ",len(city_list))
    p = 0
    for i in range(0,len(title_list)):

        title = title_list[i].text
        street = street_list[i].text
        city =  city_list[i].text
        city = city.replace(',','')
        pcode = pcode_list[i].text
        state =  state_list[i].text
        phone = phone_list[i].text
        lat = coords_list[i].find('meta',{'property':'latitude'})
        lat = str(lat['content'])
        longt = coords_list[i].find('meta',{'property':'longitude'})
        longt = str(longt['content'])
        if title.lower().find('atm') > -1:
            ltype = "ATM"
        else:
            ltype = "Branch"
        title = title.replace('\n','')
        street = street.replace('\n','')
        city = city.replace('\n','')
        state = state.replace('\n','')
        pcode = pcode.replace('\n','')
        phone = phone.replace('\n','')
        phone = phone[0:phone.find('|')]
        phone = phone.replace('.','-')
        phone = phone.rstrip()
        if len(phone) <3:
            phone = "<MISSING>"
        if len(street) <3:
            street = "<MISSING>"
        if len(city) <3:
            city = "<MISSING>"
        if len(state) <2:
            state = "<MISSING>"
        if len(pcode) <3:
            pcode = "<MISSING>"
        if state == 'West Virginia':
            state = 'WV'
       
        link = 'https://www.bankwithunited.com/contact-us?geolocation_geocoder_google_places_api='+pcode+'&geolocation_geocoder_google_places_api_state=0&field_geolocation_proximity-lat=&field_geolocation_proximity-lng=&field_geolocation_proximity=25&name=Apply#location'        
        #print(pcode, link)
        r = session.get(link, headers=headers, verify=False)
        
        soup =BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll('div',{'class':'adrs'})

        #print(len(divlist))
        hours = "<MISSING>"
        for div in divlist:            
            try:
               addr = div.find('div',{'class':'views-field-address'}).text
            except:
                try:
                    addr = div.find('span',{'class':'postal-code'}).text
                except:
                    addr = 'None'
            if addr.find(pcode) > -1 and addr != 'None':
                try:
                    hours = div.find('div',{'class':'views-field views-field-field-location-service-hour'}).text
                    if hours.find("Drive") > -1:
                        hours = hours[0:hours.find("Drive")]
                except:
                    hours = "<MISSING>"
                break
        hours = hours.replace('\n','')
        hours = hours.rstrip()
        if len(hours) < 3:
            hours = "<MISSING>"
        #print(hours)
        hours = bours.replace('Lobby: ','')        
        hours = hours.lstrip()
           
        data.append([
                        'https://www.bankwithunited.com/',
                        url,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        "<MISSING>",
                        phone,
                        ltype,
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
