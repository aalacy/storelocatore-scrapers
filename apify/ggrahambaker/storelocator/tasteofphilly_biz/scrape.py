import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import usaddress
session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    data = []
    p = 0    
    url = 'https://www.tasteofphilly.biz/locations/'   
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text,'html.parser')
    stores = soup.findAll('div',{'class':'top-menu-lr'})
   
    for store in stores:
        title = store.find('a').text
        link = 'https://www.tasteofphilly.biz'+store.find('a')['href']
        #print(p,link)
        r = session.get(link, headers=headers, verify=False)
        #print(link)
        '''if 'famous' in r.url:
            continue'''
        soup = BeautifulSoup(r.text,'html.parser')
        try:
            flag = 0
            content = soup.find('meta',{'property':'og:description'})['content']
            #print(content)
            if content.find('thanks!') > -1:
                det = content.split('thanks! ',1)[1]
            elif content.find(']') > -1:
                det = content.split('] ',1)[1]
            elif content.find('DRIVERS! ') > -1:
                det = content.split('DRIVERS! ')[1]
            elif content.find('OPEN! ',1) > -1:
                det = content.split('OPEN! ',1)[1]
            else:
                det = content
            det = det.split('Contact Us')[0]
            try:
                det = det.split(' WE DELIVER')[0]
                flag = 1
            except:
                pass
            try:
                det = det.split('(Email')[0]
            except:
                pass
            try:
                det = det.split('Hours')[0]
            except:
                pass
                    
          
            address= 'N/A'
            if len(det.rstrip().split(' ')[-1]) > 5:
                if det.find('(') > -1:
                    phone= det.rstrip().split('(')[1]
                    phone = '('+phone
                else:
                    phone= det.rstrip().split(' ')[-1]
                
            else:               
               phone= det.rstrip().split(' ')[0]
               
            address = det.replace(phone,'')
            
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
            try:
                street =street.split('!')[1]
            except:
                pass
            hours = '<MISSING>'
            try:
                hours = soup.text.split('Hours')[1]
                try:
                    hours = hours.split('Other')[0]
                except:
                    pass
                try:
                    hours = hours.split('ORDER')[0]
                except:
                    pass
                try:
                    hours = hours.split('We')[0]
                except:
                    pass
                try:
                    hours = hours.split('Contact')[0]
                except:
                    pass

                hours = hours.replace('\n',' ').lstrip().rstrip()
            except:
                pass
            lat = '<MISSING>'
            longt = '<MISSING>'
            
            try:
                coord = soup.find('iframe')['src']
                #print(coord)
                
                lat,longt = coord.split('sll=',1)[1].split('&',1)[0].split(',')
                
            except:
                if link.find('parker') > -1:
                    lat = '39.518112'
                    longt = '-104.735327'
            data.append([
                        'https://www.tasteofphilly.biz',
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
            #print(p,data[p])
            p += 1
                
        except:
            pass
        
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
