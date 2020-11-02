import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jwentertainment_com')





def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    # Your scraper here

    data = []

    pattern = re.compile(r'\s\s+')

    p = 0
    url = 'https://jwentertainment.com/locations/#'
    page = requests.get(url)
    soup = BeautifulSoup(page.text,"html.parser")
    repolist = soup.findAll("div",{'class':'location_image mb-2'})
    for div in repolist:
        store = div['id']
        store = store.replace('location_div_','')
        link = div.find('a')
        link = link['href']        
        page = requests.get(link)
        #logger.info(link)
        soup = BeautifulSoup(page.text,"html.parser")
        maindiv = soup.find('section',{'class':'event_locations'})
        title = maindiv.find('h4').text
        #logger.info(title)
        address = maindiv.find('p',{'class':'white mb-4'}).text
        #logger.info(address)
        address = usaddress.parse(address)
            #logger.info(address)
        m = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while m < len(address):
            temp = address[m]                
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]                    
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
                
            m += 1
        city = city.lstrip()
        street = street.lstrip()
        state = state.lstrip()
        pcode = pcode.lstrip()
        
        contacts = maindiv.findAll('a',{'class':'learn_more_btn w-100'})
        phone = contacts[0]['href']
        #logger.info(phone)
        coords = contacts[1]['href']        
        start = coords.find('@')+1
        end = coords.find(',',start)
        lat = coords[start:end]
        #logger.info(lat)
        start = end + 1
        end = coords.find(',',start)
        longt = coords[start:end]
        #logger.info(longt) 
        hours = maindiv.find('table',{'table table-striped timetable_locations'}).text
        hours = hours.replace('am',' am ')
        hours = hours.replace('pm',' pm ')
        hours = hours.replace('day','day : ')
        hours = hours.replace('  ',' ')
        phone = phone.replace('tel:','')
        title = title.replace(' TRAMPOLINE PARK','')
        city = city.replace(',','')
        #logger.info(hours)
        data.append([
             'https://jwentertainment.com/',
              link,
              title,
              street,
              city,
              state,
              pcode,             
              'US',
              store,
              phone,
              '<MISSING>',
              lat,
              longt,
              hours
            ])

        #logger.info(data[p])
        #p+=1
        
        
    return data        
   
    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()

