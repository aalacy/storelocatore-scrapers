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
    p = 0
    
    url = 'https://www.bankwithunited.com/location-results?field_geolocation_proximity=25&field_geolocation_proximity-lat=&field_geolocation_proximity-lng=&geolocation_geocoder_google_places_api=&geolocation_geocoder_google_places_api_state=1&full_view=true'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")

    divlist = soup.findAll('div',{'class':'adrs'})

        #print(len(divlist))
    hours = "<MISSING>"
    for div in divlist:
        title = div.find('div',{'class':'views-field-field-branch-name'}).text
       
        try:
            hours = div.find('div',{'class':'views-field views-field-field-location-service-hour'}).text
            if hours.find("Drive") > -1:
                hours = hours[0:hours.find("Drive")]
            if hours.find("Walk:") > -1:
                hours = hours[0:hours.find("Walk")]
        except:
            hours = "<MISSING>"
        ltype =''
        try:
            loc = div.find('div',{'class':'views-field-field-location-amenities'})
            #print(loc)
            loc = str(loc)
            if loc.find('brnch') > -1:
                ltype = ltype + 'Branch'
            if loc.find('atm') > -1:
                if len(ltype) < 2:
                    ltype = 'ATM'
                else:
                    ltype = ltype + "|" + 'ATM'
            
           
                        
        except:
            ltype = "<MISSING>"
        try:
            address = div.find('div',{'class':'views-field-address'})         
            state = address.find('div').text
            address = address.text
            address = address.replace('\n','')
            address = address.replace('  ','')
            state = state.lstrip()
            state = state.replace('\n','')
            state = state.replace('  ','')
            state = state.lstrip()            
            street = address.replace(state,'')
            state, pcode = state.split(',')           
        except:
            street= "<MISSING>"
            state = "<MISSING>"
            pcode = "<MISSING>"

        try:
            city = div.find('div',{'class':'views-field-title'}).text
        except:
            city = "<MISSING>"
        try:
            phone = div.find('div',{'class':'views-field-phone'}).text
            phone = phone.replace('.','-')
        except:
            phone = "<MISSING>"
        try:
            hours = div.find('div',{'class':'views-field-field-location-service-hour'}).text
            if hours.find('Drive') > -1:
                hours = hours[0:hours.find('Drive')]
            if hours.find('Walk') > -1:
                hours = hours[0:hours.find('Walk')]
            hours = hours.replace('Lobby: ','')
        except:
            hours = "<MISSING>"
        try:
            coord = str(div.find('div',{'class':'views-field-field-get-location-link'}).find('a')['href'])
            start =coord.find('@')+ 1
            end = coord.find(',',start)
            lat = coord[start : end]
            start = end + 1
            end = coord.find(',',start)
            longt = coord[start : end]
        except:
            lat =  "<MISSING>"
            longt =  "<MISSING>"
                 
        hours = hours.replace('\n','')
        hours = hours.rstrip()
        if len(hours) < 3:
            hours = "<MISSING>"
        #print(hours)
        hours = hours.replace('Lobby: ','')        
        hours = hours.lstrip()
        title = title.replace('\n','')
        title = title.lstrip()
        city = city.replace('\n','')
        city = city.lstrip()
        phone = phone.replace('\n','')
        if len(street) < 3:
            street = "<MISSING>"
        if len(pcode) < 3:
            pcode = "<MISSING>"
        if len(state) < 2:
            state = "<MISSING>"
        if len(phone) < 2:
            phone = "<MISSING>"
        phone = phone.lstrip()
        phone = phone.rstrip()
        title = title.rstrip()
        city = city.rstrip()
        state = state.replace("West Virginia","WV")
        state = state.replace("Virginia","VA")
        state = state.replace("Maryland","MD")
        state = state.replace("Ohio","OH")
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
