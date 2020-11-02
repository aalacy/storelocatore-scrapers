from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress, json

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('starbuds_us')



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
    p = 0
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.starbuds.us/locations'
    r = session.get(url, headers=headers, verify=False) 
    soup =BeautifulSoup(r.text, "html.parser")   
    linklist = soup.findAll('a')
    citylist = []
    streetlist = []
    for link in linklist:
        if link.text.find('LOCATION') > -1 and link['href'] != 'https://www.starbuds.us/locations':
            #title = link.text
            mlink = link['href']
            #logger.info(mlink)
            r = session.get(mlink, headers=headers, verify=False)
            soup = BeautifulSoup(r.text,'html.parser')
            newlist = soup.findAll('a')            
            for nowlink in newlist:
                if nowlink.text.find('VIEW HOURS, SPECIALS AND MENU') > -1:
                    if nowlink not in citylist:
                        citylist.append(nowlink)

            
            if len(citylist) == 0 and link not in citylist:
                citylist.append(link)
                
                
    for city in citylist:
        nowlink = city['href']
        #logger.info(nowlink)
                         
        r = session.get(nowlink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text,'html.parser')
        
        hours = soup.text.split("HOURS",1)[1].split('DAILY SPECIALS',1)[0].replace('\n',' ').lstrip()
        try:
            content = r.text.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0]                    
            content = content.replace('\n','')
            content = json.loads(content)
           
            title = content['name']
            street = content["address"]["streetAddress"]
            if street in streetlist:
                content = content.text
            else:
                streetlist.append(street)
            state = content["address"]["addressRegion"]
            pcode = content["address"]["postalCode"]
            city = content["address"]["addressLocality"]
            lat  = content["areaServed"]["geoMidpoint"]['latitude']
            longt = content["areaServed"]["geoMidpoint"]['longitude']
            phone = content["telephone"].replace('+','').replace('+1','')
            #logger.info(phone)
            if phone[0] == '1':
                phone = phone[1:4]+'-'+phone[4:7]+'-'+phone[7:11]
            else:   
                phone = phone[0:3]+'-'+phone[3:6]+'-'+phone[6:10]
        except:
            
            title = soup.find('title').text.split('|')[0]
            if title.find('Star Buds') > -1:
                title= soup.find('title').text.split('|')[1]
            divlist = soup.findAll('a')
            phone = '<MISSING>'
            coord = '<MISSING>'
            address = '<MISSING>'
            for div in divlist:
                try:
                    if div['href'].find('tel') > -1:
                        phone = div.text
                    elif div['href'].find('/maps/place') > -1:
                        coord = div['href']
                        
                except:
                    pass
                    
            ps = soup.find_all('p', {'class': 'font_7'})
            address = ps[0].text.replace(u'\xa0', ' ')
            try:
                lat,longt = coord.split('!3d',1)[1].split('!4d')
            except:
                lat = longt = '<INACCESSIBLE>'
            
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
                

        data.append([
                    'https://www.starbuds.us',
                    nowlink,                   
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
                    hours.replace("\xa0",' ')
                ])
        ##logger.info(p,data[p])
        p += 1
            
        
            
     
           
        
    return data


def scrape():    
    data = fetch_data()
    write_output(data)
    

scrape()
