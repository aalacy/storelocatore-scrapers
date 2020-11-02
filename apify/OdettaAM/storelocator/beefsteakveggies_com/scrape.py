import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('beefsteakveggies_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain",'page_url', "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data=[]
    p =0
    url = "http://beefsteakveggies.com/where-we-are/"
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll('a',{'class':'card__btn'})
    for link in linklist:
        link = 'https://www.beefsteakveggies.com'+ link['href']
        #logger.info(link)
        r = session.get(link, headers=headers, verify=False)
  
        soup =BeautifulSoup(r.text, "html.parser")
        maindiv = soup.find('section',{'id':'intro'})
        title = maindiv.find('h2').text
        #logger.info(title)
        address = maindiv.find('a',{'data-bb-track-category':'Address'}).text
        address = address.lstrip()
        address = address.replace('\n','')
        #logger.info(address)
        address = address.replace(',',' ')
        address = usaddress.parse(address)
        #logger.info(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("Occupancy") != -1 or  temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1

        #logger.info(city)
        street = street.lstrip()
        street = street.replace(',','')
        city = city.lstrip()
        city = city.replace(',','')
        state = state.lstrip()
        state = state.replace(',','')
        pcode = pcode.lstrip()
        pcode = pcode.replace(',','')
       

        #logger.info(street)
        try:
            phone = maindiv.find('a',{'data-bb-track-category':'Phone Number'}).text
        except:
            phone = "<MISSING>"
        coords = soup.find('div',{'class':'gmaps'})
        lat = coords['data-gmaps-lat']
        longt = coords['data-gmaps-lng']
        #logger.info(lat)
        hours = soup.find('div',{'class':'col-md-6'})
        hours = hours.findAll('p')
        hours = hours[1].find('strong').text
        #logger.info(hours)
        data.append(['http://beefsteakveggies.com',link,title,street,city,state,pcode,'US',"<MISSING>",phone,"<MISSING>",lat,longt,hours])
        #logger.info(p,data[p])
        p += 1

    return data
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
