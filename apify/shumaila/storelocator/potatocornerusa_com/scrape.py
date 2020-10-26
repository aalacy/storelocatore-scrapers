from bs4 import BeautifulSoup
import csv
import string
import re, time, json
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('potatocornerusa_com')



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
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://www.potatocornerusa.com/store-locator'
    p = 0
    r = session.get(url, headers=headers, verify=False)    
    r = r.text.split(':{"pages":')[1].split('],"mainPageId"')[0]
    r = r + ']'
    loclist = json.loads(r)
    titlelist = []
    titlelist.append('none')
    for loc in loclist:
        #logger.info(loc)
        title = loc['title']
        if title.find('Locations') > -1:
            slink = 'https://www.potatocornerusa.com/'+loc['pageUriSEO']
            #logger.info(slink)
            
            r = session.get(slink, headers=headers, verify=False)
            soup = BeautifulSoup(r.text,'html.parser')
            linklist = soup.findAll('h6')           
            for link in linklist:                
                try:
                    link = link.find('a')['href']
                except:
                    continue                
                if link == 'https://www.potatocornerusa.com':
                    continue                
                page = session.get(link, headers=headers, verify=False)                
                soup1 = BeautifulSoup(page.text,'html.parser')               
                try:
                    title = soup1.find('title').text.split('|')[0]
                except:
                    try:
                        title = soup1.find('meta',{'property':"og:title"})['href']
                    except:
                        try:
                            title = soup1.find('h3').text
                        except:
                            title = 'mm'
                            page = session.get(link, headers=headers, verify=False)
                            time.sleep(5)
                            soup1 = BeautifulSoup(page.text,'html.parser')
                            title = soup1.find('title').text.split('|')[0]
                            pass
               
                if title.find('Coming Soon') == -1 and title not in titlelist:
                    titlelist.append(title)
                    phone = 'N/A'
                    divlist = soup1.findAll('div')
                    for div in divlist:
                        if div.text.find('Address') > -1 and div.text.find('Phone') > -1:
                            dtext = re.sub(cleanr,'',str(div))
                            #logger.info(dtext)
                            address = dtext.split('Address:',1)[1].split('Phone')[0].replace('\n',' ')
                            phone = dtext.split('Phone',1)[1].split(':',1)[1].split('#mask')[0]                           
                            
                            break
                  
                    datalink = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?f=json&SingleLine='+title.replace(' ','%20')+'&outfields=placeName,place_addr,phone,url,location'
                    pagedata = session.get(datalink, headers=headers, verify=False).json()["candidates"][0]
                    coord = pagedata['location']
                    longt = str(coord['x'])
                    lat = str(coord['y'])
                    if phone == 'N/A':
                        phone = '<MISSING>'
                    else:
                        phone = phone.replace("\u200e",'').replace("\xa0",'')                                     
                    address = usaddress.parse(address.replace('Address: ',''))
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
                    if len(pcode) < 2:
                        pcode = '<MISSING>'
                    lat = lat[0:5]
                    longt = longt[0:7]
                    if len(street) < 3:
                        street = title
                    data.append([
                        'https://www.potatocornerusa.com/',
                        link,                   
                        title,
                        street.replace('\\xa','').replace('Address:','').lstrip(),
                        city.replace('\\xa',''),
                        state.replace('\\xa',''),
                        pcode.replace('\\xa',''),
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        '<MISSING>'
                    ])
                    #logger.info(p,data[p])                    
                    p += 1
                   
     
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

