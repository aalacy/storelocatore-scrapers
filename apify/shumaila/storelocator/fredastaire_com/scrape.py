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
    data = []
    p  =0 
    url = 'https://www.fredastaire.com/locations/'
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split('"places":',1)[1].split('],"map_tabs":',1)[0]
    loclist = loclist +']'
    loclist = json.loads(loclist)
    for loc in loclist:
        #print(loc)
        store = loc['id']
        title = loc['title']
        address = loc['address']
        lat = loc['location']['lat']
        longt = loc['location']['lng']        
        phone = loc['location']['extra_fields']['location-phone-number']
        link = loc['location']['extra_fields']['custom-location-link']
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

        city = loc['location']['city']
        try:
            state = loc['location']['state']
        except:
            continue
        ccode = loc['location']['country']
        pcode = loc['location']['postal_code'].replace('','')
        street = street.lstrip().replace(',','')
        city = city.lstrip().replace(',','')
        state = state.lstrip().replace(',','')
        pcode = pcode.lstrip().replace(',','')
        
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
