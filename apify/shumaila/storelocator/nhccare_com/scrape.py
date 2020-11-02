import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from sgrequests import SgRequests
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('nhccare_com')



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
    
    
    url = 'https://nhccare.com/find-a-community/'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    state_list = soup.findAll('a', {'class': 'avia-button'})
    logger.info("states = ",len(state_list))
    p = 0
    for state in state_list:
        #logger.info(state.text)    
        state = state['href']
        divlist = []
        linklist = []
        r = session.get(state, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        a_list = soup.findAll('a')
        divlist = soup.findAll('div',{'class':'entry-content-wrapper'})
        for div in divlist:
            
            if div.text.find('Address') > -1 or div.text.find('Phone') > -1:
                link = div.find('a',{'class':'avia-button'})['href']
                if link.find('https://nhccare.com/locations/') > -1:
                    address = ''
                    phone = 'N/A'
                    title = div.find('h1').text
                                  
                    textlist = div.findAll('div',{'class':'avia_textblock'})
                    address= textlist[0].text               
                    mstart = address.find('\n')+1
                    mstart = address.find('\n',mstart)+1
                    address = address[mstart:len(address)]
                    address = address.replace('\n',' ')
                    if address.find('License') > -1:
                        address = address[0:address.find('License')]
                    
                    phone = textlist[1].text
                    phone = phone.splitlines()
                    phone = phone[1]                
                    address= usaddress.parse(address)
                    street = ""
                    state = ""
                    city = ""
                    pcode = ""
                    i = 0
                    while i < len(address):
                        temp = address[i]
                        if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("Occupancy") != -1 or  temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                            street = street + " " + temp[0]
                        if temp[1].find("PlaceName") != -1:
                            city = city + " " + temp[0]
                        if temp[1].find("StateName") != -1:
                            state = state + " " + temp[0]
                        if temp[1].find("ZipCode") != -1:
                            pcode = pcode + " " + temp[0]
                        i += 1
                    if len(street) < 2 :
                        street = 'N/A'
                    if len(city) < 2:
                        city = 'N/A'
                    if len(state) < 1:
                        state = 'N/A'
                    if len(pcode) < 3:
                        pcode = 'N/A'
                    street = street.lstrip()
                    pcode = pcode.lstrip()
                    city = city.lstrip()
                    state = state.lstrip()
                    city = city.replace(',','')
                    link = div.find('a',{'class':'avia-button'})['href']
                    #logger.info(link)
                    r1 = session.get(link, headers=headers, verify=False)
                    soup1 = BeautifulSoup(r1.text, "html.parser")
                    coordlist = soup1.findAll('a')
                    soup1 = str(soup1)
                    coords = 'N/A'
                    lat = '<MISSING>'
                    longt = '<MISSING>'
                    for coord in coordlist:
                        if coord['href'].find('https://www.google.com/maps/place/') > -1 and coord['href'].find('@') > -1:
                            coords = coord['href']
                            break
                        
                    if coords != 'N/A':
                        start = coords.find('@')+1
                        end = coords.find(',',start)
                        lat = coords[start:end]
                        start = end +1
                        end = coords.find(',',start)
                        longt = coords[start:end]
                    else:
                       start = soup1.find("['long']")
                       if start != -1:
                           start = soup1.find('=',start) + 2
                           end = soup1.find(';',start)
                           longt = soup1[start:end]
                           start = soup1.find("['lat']")
                           start = soup1.find('=',start) + 2
                           end = soup1.find(';',start)
                           lat = soup1[start:end]
                   
                    data.append(['https://nhccare.com',link,title,street,city,state,pcode,'US',"<MISSING>",phone,"<MISSING>",lat,longt,"<MISSING>"])
                    #logger.info(p,data[p])
                    p += 1
                    #input()
                        
  
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
