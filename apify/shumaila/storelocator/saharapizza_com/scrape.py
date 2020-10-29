from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('saharapizza_com')



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
    cleanr = re.compile(r'<[^>]+>')
    data = []
    p = 0
    url = 'https://saharapizza.com/locations/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.find('table').findAll('tr')
    for div in divlist:
        det = div.findAll('td')
        if len(det) > 2:
            try:
                title = det[0].text.split('(')[0]
            except:
                title = det[0].text
            if title.find('Bolivia') == -1:
                address = re.sub(cleanr,' ',str(det[1])).strip()
                #logger.info(address)
                #input()
                if len(address) > 5 and address.find('CLOSED') == -1:
                    address = usaddress.parse(address)
                    #logger.info(address)
                    i = 0
                    street = ""
                    city = ""
                    state = ""
                    pcode = ""
                    while i < len(address):
                        temp = address[i]
                        if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Subaddress") != -1  or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find('Occupancy') != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                            street = street + " " + temp[0]
                        if temp[1].find("PlaceName") != -1:
                            city = city + " " + temp[0]
                        if temp[1].find("StateName") != -1:
                            state = state + " " + temp[0]
                        if temp[1].find("ZipCode") != -1:
                            pcode = pcode + " " + temp[0]
                        i += 1

                else:
                    street = '<MISSING>'
                    city = '<MISSING>'
                    pcode = '<MISSING>'
                    state = '<MISSING>'
                phone = det[2].text
                if city.find('A ') > -1:
                    street = street  + ' A'
                    city = city.replace('A ','')
                try:
                    phone = phone.split('ORDER ONLINE!')[0]
                except:
                    pass
                try:
                    phone = phone.split('Bow')[0]
                except:
                    pass
                if len(phone) < 3:
                    phone = '<MISSING>'
                data.append([
                        'https://saharapizza.com/',
                        'https://saharapizza.com/locations/',                   
                        title.replace('\xa0\xa0',''),
                        street.lstrip().replace(',',''),
                        city.lstrip().replace(',',''),
                        state.lstrip().replace(',',''),
                        pcode.lstrip().replace(',',''),
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>'
                    ])
                #logger.info(city)
                #logger.info(p,data[p])
                p += 1
                

   
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
