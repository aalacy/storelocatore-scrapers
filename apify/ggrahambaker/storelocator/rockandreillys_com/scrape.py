import csv, re
import os
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import usaddress
session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

cleanr = re.compile(r'<[^>]+>')

def retaddr(address):
    address = address.replace(',','').replace('\n','')
    address = usaddress.parse(address)
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
    street = street.lstrip()
    city = city.lstrip()
    state = state.lstrip()
    pcode = pcode.lstrip()

    return street,city,state,pcode

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def usc_parse(link, locator_domain):
    
    r = session.get(link, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
    maindiv = soup.find('section',{'id':'intro'}).findAll('p')
    total = len(maindiv)
    hours = ' '
    det = maindiv[0].findAll('a')
    address = det[0].text.lstrip()
    street_address,city,state = address.split(', ',2)
    state = state.lstrip()
    state , zip_code = state.split(' ',1)
    phone_number = det[1].text
    
    
    for i in range(1,len(maindiv)):
        hours = hours + maindiv[i].text + ' '

    

    country_code = 'US'
    location_type = '<MISSING>'
    store_number = '<MISSING>'
    longit = '<MISSING>'
    lat = '<MISSING>'

    store_data = [locator_domain,link, 'USC', street_address, city, state, zip_code.replace('\t','').replace('\n','').rstrip(), country_code,
                  store_number, phone_number, location_type, lat, longit, hours]

    #print(store_data)
    return store_data

def sunset_parse(link, locator_domain):
    r = session.get(link, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
    store_data = []
    det = []
    #sections = driver.find_elements_by_css_selector('section')
    sections = soup.findAll('div')
    for section in sections:
        if 'Address' in section.text:
            det = section.findAll('p')
        elif 'Hour' in section.text:
            det1 = section.find('p')
            
   
    address = det[0]
    address =cleanr.sub('\n', str(address)).splitlines()
    street_address = address[1]
    city,state = address[2].split(', ',1)
    state = state.lstrip()
    state ,zip_code = state.split(' ',1)
    phone_number = address[3]
    
    
    hours =cleanr.sub(' ', str(det1))   
    location_name = 'Sunset'
    country_code = 'US'
    location_type = '<MISSING>'
    store_number = '<MISSING>'
    longit = '<MISSING>'
    lat = '<MISSING>'

    store_data = [locator_domain,link, location_name, street_address, city, state, zip_code, country_code,
             store_number, phone_number, location_type, lat, longit, hours ]

    #print("SUNSET",store_data)
    return store_data

def vegas_parse(link, locator_domain):
    # las vegas
    
    
    detail = []
    r = session.get(link, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
    detail = soup.findAll('div',{'class':'footer-txt'})
    

    #print(detail)
    address = detail[0]
    address =cleanr.sub(' ', str(address)).replace('\t','').replace('\r','')    
    #print(detail[1].text)
    street_address,city,state,zip_code = retaddr(address)  
    phone_number =  detail[1].text.replace('\t','').replace('\r','').replace('\n','')          

    hours = '<MISSING>'
    #phone_number = driver.find_element_by_css_selector('div.footer-item').text.split('\n')[-1]
   
    location_name = 'Las Vegas'
    country_code = 'US'
    location_type = '<MISSING>'
    store_number = '<MISSING>'
    longit = '<MISSING>'
    lat = '<MISSING>'

    store_data = [locator_domain,link, location_name, street_address, city, state, zip_code, country_code,
                  store_number, phone_number, location_type, lat, longit, hours]

    #print("LAS VEGAS",store_data)
    return store_data

def fetch_data():
    locator_domain = 'rockandreillys.com/'
    las_vegas = 'http://www.rockandreillyslv.com/'
    sunset = 'https://rockandreillys.com/'
    usc = 'https://www.rockandreillysusc.com/location/Rock-n-Reillys-USC/'
    
   
    vegas_list = vegas_parse(las_vegas, locator_domain)
    sunset_list = sunset_parse(sunset, locator_domain)
    usc_list = usc_parse(usc, locator_domain)

    all_store_data = [vegas_list, sunset_list, usc_list]

   
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
