import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bankwithunited_com')



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

        #logger.info(len(divlist))
    hours = "<MISSING>"
    flag = 0
    for div in divlist:
        try:
            title = div.find('div',{'class':'views-field-field-branch-name'}).text
        except:
            try:
                title = div.find('div',{'class':'field--name-field-branch-name'}).text                
                
            except:
                title = '<MISSING>'
       
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
            #logger.info(loc)
            loc = str(loc)
            if loc.find('brnch') > -1:
                ltype = ltype + 'Branch'
            if loc.find('atm') > -1:
                if len(ltype) < 2:
                    ltype = 'ATM'
                else:
                    ltype = ltype + "|" + 'ATM'
            
           
                        
        except:
            try:
                loc = div.find('div',{'class':'field--name-field-location-amenities'}).text
            #logger.info(loc)
                loc = str(loc)
                if loc.find('Branch') > -1:
                    ltype = ltype + 'Branch'
                if loc.find('ATM') > -1:
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
            try:
                street = div.find('span',{'class':'address-line1'}).text
            except:
                street= "<MISSING>"
            try:
                city = div.find('span',{'class':'locality'}).text
            except:
                city =  "<MISSING>"
                    
            try:
                state = div.find('span',{'class':'administrative-area'}).text
            except:
                state= "<MISSING>"
            try:
                pcode = div.find('span',{'class':'postal-code'}).text
            except:
                pcode = "<MISSING>"

        try:
            city = div.find('div',{'class':'views-field-title'}).text
        except:
            if city == "<MISSING>":
                try:
                    city = div.find('span',{'class':'field-content'}).text 
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
            #logger.info(coord)
            #input()
            start =coord.find('@')
            if start > -1 :
                start = start + 1
                end = coord.find(',',start)
                lat = coord[start : end]
                start = end + 1
                end = coord.find(',',start)
                longt = coord[start : end]
            else:
                start = coord.find('3d')
                if start > -1:
                    start = start + 2
                    end = coord.find('%',start)
                    lat = coord[start : end]
                    start = coord.find('-',start)
                    end = len(coord)
                    longt = coord[start : end]
                    
                    
                else:
                    lat =  "<MISSING>"
                    longt =  "<MISSING>"
                    
        except Exception as e:            
            
            lat =  "<MISSING>"
            longt =  "<MISSING>"
        
                 
        hours = hours.replace('\n','')
        hours = hours.rstrip()
        if len(hours) < 3:
            hours = "<MISSING>"
        #logger.info(hours)
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
        if len(lat) < 2:
            lat = "<MISSING>"
        if len(longt) < 2:
            longt = "<MISSING>"
        if len(ltype) < 2:
            ltype = "<MISSING>"
        phone = phone.lstrip()
        phone = phone.rstrip()
        title = title.rstrip()
        city = city.rstrip()
        state = state.replace("West Virginia","WV")
        state = state.replace("Virginia","VA")
        state = state.replace("Maryland","MD")
        state = state.replace("Ohio","OH")
        hours = hours.replace('\r',' ')
        
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
        #logger.info(p,data[p])
        p += 1
                

                
                
            
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
