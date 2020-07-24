from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from sgrequests import SgRequests

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
    p = 0
    url = 'https://www.sleepexperts.com/stores'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    store_list = soup.findAll('div', {'class': 'StorePromo'})
    print("states = ",len(store_list))
    for store in store_list:
        title = store.find('div',{'class':'StorePromo-title'}).text
        address = store.find('div',{'class':'StorePromo-address'}).text
        coord = 'https://www.google.com/maps/place/'+address.replace(' ','+')
        try:
            phone = store.find('div',{'class':'StorePromo-phoneNumber'}).text
        except:
            phone = '<MISSING>'
        try:
            hours = store.find('div',{'class':'StorePromo-condensedHours'}).text
        except:
            hours ='<MISSING>'
        link  = store.find('a',{'class':'StorePromo-cta'})['href']
        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        data.append(['https://www.sleepexperts.com/',link,title,
                        street.lstrip().replace(',',''),
                        city.lstrip().replace(',',''),
                        state.lstrip().replace(',',''),
                        pcode.lstrip().replace(',',''),
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        '<INACCESSIBLE>',
                        '<INACCESSIBLE>',
                        hours.replace('\n','')
                    ])
        print(p,data[p])
        p += 1
        

    return data        
        
   
def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
