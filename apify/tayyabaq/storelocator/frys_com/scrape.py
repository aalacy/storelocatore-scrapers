import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re, time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('frys_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\&ll=([\d\.]*)', url)[0]
    return lat,lon

def fetch_data():
    data=[]; location_name=[];links=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]

    base_link = 'https://www.frys.com/ac/storeinfo/storelocator/?site=csfooter_B'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)

    base = BeautifulSoup(req.text,"lxml")

    location = base.find(id="submenu-stores").find_all('a', {'href': re.compile(r'/ac/storeinfo/.+hours-maps-directions')})
    location_href=["https://www.frys.com" + location[n]['href'] for n in range(0,len(location))]

    for n in range(0,len(location_href)):
        link = location_href[n]
        links.append(link)
        # logger.info(link)
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")
        location_name.append(base.find(id='text1').text.strip())
        address = list(base.find(id='address').stripped_strings)
        street_address.append(address[0])
        city.append(address[1].split(",")[0])
        state.append(address[1].split(",")[1].split()[0])
        zipcode.append(address[1].split(",")[1].split()[1])
        phone.append(address[2].split("Phone ")[1])
        try:
            lat_lon= base.find("a", string="Google Map")
            lat,lon=parse_geo(str(lat_lon['href']))
            if (lat=="") or (lat==[]):
                latitude.append('<MISSING>')
            else:
                latitude.append(lat)
            if (lon=="") or (lon==[]):
                longitude.append('<MISSING>')
            else:
                longitude.append(lon)
        except:
            map_link = lat_lon['href']
            if "@" in map_link:
                at_pos = map_link.rfind("@")
                latitude.append(map_link[at_pos+1:map_link.find(",", at_pos)].strip())
                longitude.append(map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip())
            else:
                try:                    
                    req = session.get(map_link, headers = HEADERS)
                    maps = BeautifulSoup(req.text,"lxml")
                    raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
                    latitude.append(raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip())
                    longitude.append(raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip())
                except:
                    latitude.append('<MISSING>')
                    longitude.append('<MISSING>')
    for n in range(0,len(street_address)): 
        data.append([
            'https://www.frys.com',
            links[n],
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            '<INACCESSIBLE>'
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
