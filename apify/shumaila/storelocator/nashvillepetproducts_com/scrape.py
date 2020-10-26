import time
import csv
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import usaddress

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
    data=[]
    stlist = []
    stlist.append('none')
    p = 0
    url = 'http://nashvillepetproducts.com/locations/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    time.sleep(8)
    stores = soup.findAll('div',{'class':'elementor-widget-wrap'})
    count = 1
    for store in stores:
        
        try:
            title = store.find('h1').text          
          
            if store.find('div',{'class':'elementor-text-editor'}).text.find('Address') == -1:
                #print("No")
                pass
            else:
                #print("YES")               
                l = store.find('p').text 
                page_url = "http://nashvillepetproducts.com/locations/"
                info = store.find('div',{'class':'elementor-text-editor'})
                info = cleanr.sub(' ', str(info))
                info = info.replace('  ',' ')
                
                              
                address = info[0:info.find('(')]
                address = address.replace('Address','')
                address = address.lstrip()
                address = usaddress.parse(address)
                i = 0
                street = ''
                city=''
                state = ''
                pcode = ''
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

                street = street.lstrip()
                pcode = pcode.lstrip()
                city = city.lstrip()
                state = state.lstrip()
                
                phone = info[info.find(')'):info.find('Hours')]
                phone = phone.lstrip()
                hours = info[info.find('Hours'):len(info)]
                hours = hours.replace('Hours','')
                hours = hours.lstrip()                              
                phone = phone[phone.find(' ')+ 1:len(phone)]
                phone = phone.lstrip()
                phone = phone.replace('.','-')
                
                city = city.replace(',','')
                
                if street in stlist:
                    pass
                else:
                    stlist.append(street)
                    data.append([
                     'http://nashvillepetproducts.com/',
                      page_url,
                      title,
                      street,
                      city,
                      state,
                      pcode,
                      'US',
                      '<MISSING>',
                      phone,
                      '<MISSING>',
                      '<MISSING>',
                      '<MISSING>',
                      hours
                    ])
                
                    #print(p,data[p])
                    p += 1
            
        except Exception as e:
            #print(e)
            pass
           

   
   
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
