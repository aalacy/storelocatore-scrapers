from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('neighborstop_com')



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
    links = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.neighborstop.com/locations'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=locations]")   
    p = 0
    for link in linklist:
        
        if link['href'] in links or link['href'] == '/locations':
            continue
        links.append(link['href'])
        link = 'https://www.neighborstop.com' + link['href']        
        r = session.get(link, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        title = soup.find('h1').text
        phone = soup.find('div',{'jscontroller':'Ae65rd'}).text
        #address = soup.find('div',{'jscontroller':'Ae65rd'}).text.replace('\n',' ')
        hourlist = soup.findAll('h2')
        address = hourlist[0].text
        
        hours = hourlist[1].text + ' '+hourlist[2].text
        lat,longt = soup.find('iframe',{'jsname':'L5Fo6c'})['src'].split('&ll=',1)[1].split('&',1)[0].split(',')
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
        if street.find('Circle Pines') > -1 and len(city) < 3:
            city = 'Circle Pines'
        data.append([
                        'https://www.neighborstop.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        hours
                    ])
        #logger.info(p,data[p])
        p += 1
                
       
        
           
        
    return data


def scrape():   
    data = fetch_data()
    write_output(data)
    

scrape()
