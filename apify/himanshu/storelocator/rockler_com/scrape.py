import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.rockler.com"
    return_main_object = []
    soup = BeautifulSoup(session.get(base_url+'/retail/stores').text,'lxml')
    output=[]
   
    for dt in soup.find('ul',{'class':'cms-menu'}).find('ul').find_all('li')[:-1]:
        st = dt.find('a')['href']
        
        soup1 = BeautifulSoup(session.get(st).text,'lxml')
        
        main1 = soup1.find('ul',{"class":'cms-menu'}).find('ul').find_all('a')
    
        for dt1 in main1:
            if dt1['href'] == "https://www.rockler.com/retail/stores/wi":
                page_url = "https://www.rockler.com/retail/stores/wi/brookfield-store"
            else:
                page_url = dt1['href']
           
            soup2 = BeautifulSoup(session.get(page_url).text, 'lxml')

            if page_url == "https://www.rockler.com/retail/stores/wi/brookfield-store":
                main2 = soup2.find("div",{"class":"col-m-5"})
            elif page_url == "https://www.rockler.com/retail/stores/wa/tukwila-store":
                main2 = soup2.find_all("div",{"class":"col-m-6"})[1]
            else:
                main2 = soup2.find("div",{"class":"col-m-6"})

            loc = list(main2.stripped_strings)
            if '**New Address**' in loc:
                loc.remove('**New Address**')
                loc.remove('Store Location')
               
            hours = " ".join(loc[loc.index("Store Hours"):])
            
            name = loc[0].strip()
            i = loc.index('Phone:')
            if i>3:
                del loc[1]

            address = loc[1].strip()
            addr = loc[1].split(',')
            if len(addr) == 2 and i == 2:
                state = addr[-1].strip().split(' ')[0]
                zipp = addr[-1].strip().split(' ')[1]
                adr = addr[0].strip().split(' ')
                city = adr[-1].strip()
                del adr[-1]
                address = ' '.join(adr)
                phone = loc[3].strip()
            else:
                ct = loc[2].split(',')
                
                city = ct[0].strip()
                state = ct[1].strip().split(' ')[0].strip()
                zipp = ct[1].strip().split(' ')[1].strip()
                phone = loc[4].strip()

            if "Suite 006-B" in address:
                address = "2000 Park Manor Blvd" + " " + loc[1]

            storeno = ''
            lat = soup2.find('h3', text="Store Hours").parent.parent.parent.find('iframe')['src'].split('!3d')[1].split('!')[0].strip()
            lng = soup2.find('h3', text="Store Hours").parent.parent.parent.find('iframe')['src'].split('!2d')[1].split('!')[0].strip()
            
            country = "US"
           
            store = []
            store.append(base_url)
            store.append(name if name else "<MISSING>")
            store.append(address if address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country if country else "<MISSING>")
            store.append(storeno if storeno else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("rockler")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hours if hours.strip() else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            ads = address + ' ' + city + ' ' + state + ' ' + zipp
            if ads not in output:
                output.append(ads)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

