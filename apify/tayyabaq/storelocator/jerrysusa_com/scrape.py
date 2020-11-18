from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress

from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
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
    p = 0
    data = []
    
    url = 'https://api.storepoint.co/v1/15a57988e54ad0/locations?'
    loclist = session.get(url, headers=headers, verify=False).json()['results']['locations']
    for loc in loclist:        
        store = loc['id']
        lat = loc['loc_lat']
        longt = loc['loc_long']
        title = loc['name']
        phone = loc['phone']
        address = loc['streetaddress']
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
        if len(loc['monday']) < 2:
            hours = '<MISSING>'
        else:
            hours = 'Monday '+ loc['monday']+' Tuesday '+loc['tuesday']+' Wednesday '+loc['wednesday']+' Thursday '+loc['thursday']+ ' Friday '+loc['friday']+' Saturday '+loc['saturday']+' Sunday '+loc['sunday']
        
        if len(phone) < 3:
            phone = '<MISSING>'
                
        data.append(['https://jerrysusa.com/','https://jerrysusa.com/store-locator/',title,street,city,state,pcode,'US',store,phone,'<MISSING>',lat,longt,hours
                    ])
        #print(p,data[p])
        p += 1
                

                
                
            
        
    return data


def scrape():    
    data = fetch_data()
    write_output(data)
    

scrape()
