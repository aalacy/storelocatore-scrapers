import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
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
    
    url = 'https://www.fredastaire.com/locations/'
    r = session.get(url, headers=headers, verify=False)
    time.sleep(2)
    soup = BeautifulSoup(r.text,'html.parser')
    soup = str(soup.find('div',{'class':'entry-content'}).find('script').text)
    start = soup.find('"places"')
    start = soup.find(':',start)
    end = soup.find('}],"map_tabs"')
    #print(start ,end)
    soup = soup[start:end]
    soup = soup.replace(',"map_tabs"','')
    start = 0
    p = 0
    while True:
        start = soup.find('{',start)
        if start == -1:
            break
        end = soup.find('}',start)+1
        strm = soup[start :end]
               
        mstart = 0
        mstart = strm.find('"id"')
        mstart = strm.find(':',mstart)+ 1
        mend = strm.find(',',mstart)
        store = strm[mstart:mend]
        store = store.replace('"','')
        
        if store == '1':
            
            start = soup.find('{',end)
            if start == -1:
                break
            end = soup.find('}',start)+1
            strm = soup[start :end]
            mstart = 0
            mstart = strm.find('"id"')
            mstart = strm.find(':',mstart)+ 1
            mend = strm.find(',',mstart)
            store = strm[mstart:mend]
            store = store.replace('"','')
           
        mstart = strm.find('"title"')
        mstart = strm.find(':',mstart)+ 1
        mend = strm.find(',',mstart)
        title = strm[mstart:mend]
        title = title.replace('"','')
        mstart = strm.find('"address"')
        mstart = strm.find(':',mstart)+ 2
        mend = strm.find('"',mstart)
        address = strm[mstart:mend]
        #address = address.replace('"','')
        mstart = strm.find('"lat"')
        mstart = strm.find(':',mstart)+ 1
        mend = strm.find(',',mstart)
        lat = strm[mstart:mend]
        lat = lat.replace('"','')
        mstart = strm.find('"lng"')
        mstart = strm.find(':',mstart)+ 1
        mend = strm.find(',',mstart)
        longt = strm[mstart:mend]
        longt = longt.replace('"','')
        mstart = strm.find('"city"')
        mstart = strm.find(':',mstart)+ 1
        mend = strm.find(',',mstart)
        city = strm[mstart:mend]
        city = city.replace('"','')
        mstart = strm.find('"state"')
        mstart = strm.find(':',mstart)+ 1
        mend = strm.find(',',mstart)
        state = strm[mstart:mend]
        state = state.replace('"','')
        mstart = strm.find('"postal_code"')
        mstart = strm.find(':',mstart)+ 1
        mend = strm.find(',',mstart)
        pcode = strm[mstart:mend]
        pcode = pcode.replace('"','')
        mstart = strm.find('"location-phone-number"')
        mstart = strm.find(':',mstart)+ 1
        mend = strm.find(',',mstart)
        phone = strm[mstart:mend]
        phone = phone.replace('"','')
        mstart = strm.find('"country"')
        mstart = strm.find(':',mstart)+ 1
        mend = strm.find(',',mstart)
        ccode = strm[mstart:mend]
        ccode = ccode.replace('"','')
        mstart = strm.find('"custom-location-link"')
        mstart = strm.find(':',mstart)+ 1
        mend = strm.find(',',mstart)
        link = strm[mstart:mend]
        link = link.replace('"','')
        
        #print(address)
        address = usaddress.parse(address)
        #print(address)
        
        i = 0
        street = ""        
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("OccupancyType") != -1 or temp[1].find("OccupancyIdentifier") != -1 or temp[1].find("Recipient") != -1 or \
                    temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1:
                street = street + " " + temp[0]
           
            i += 1
        
       
        street = street.lstrip()
        street = street.replace(',','')
        start = end + 1
        #print(street)
        street = street.replace('\\','')
        #input()
        
        link = link.replace('\\','')
        if len(pcode) > 5:
            pcode = pcode[0:len(pcode)-1]
        if state == 'Wisconsin':
            state = 'WI'
        if len(phone) < 3:
            phone = "<MISSING>"
        if ccode == "United States" and link.find('COMING SOON') == -1:
            data.append(['https://www.fredastaire.com/',link,title,street,city,state,pcode,'US',store,phone,"<MISSING>",lat,longt,"<MISSING>"])
            #print(p,data[p])
            p += 1
            
   
    return data 
    
    
    

def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
