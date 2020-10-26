import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://myspire.com"

    a = 0
    while a < 4:
        a += 1 # Same as a = a + 1     
        location_url = base_url+'/Branches-ATMs?page='+str(a)
        r = session.get(location_url,headers = header)
        soup = BeautifulSoup(r.text,"lxml")
        v = soup.find_all('div',{'class':'locationTXT'})
        for target_list in v:

            locator_domain = base_url
            location_name = target_list.find('h3',{'class':'locationheadingTXT'}).find('a').text
            gk =  target_list.find('p',{'class':'locationsHoursTXTaddress'}).text.strip().split('\n')
            coor = target_list.find('a')['href'].replace('/Branches-ATMS?','').replace('radius=100','').replace('&',' ').split(' ')

            street_address = gk[0].strip()
            city = gk[1].strip().split(',')[0]
            state =  gk[1].strip().split(',')[1].strip().split(' ')[0]
            zip  = gk[1].strip().split(',')[1].strip().split(' ')[1]
            country_code = 'USA'
            location_type = 'myspire'
            store_number = '<MISSING>'
            phone = '<MISSING>'

            latitude = coor[0].replace('lat=','')
            longitude =  coor[1].replace('lng=','')
            ck =  target_list.find('p',{'class':'locationsHoursTXT'}).text.strip().split('\n')
            hours_of_operation = ck[0] +' , '+ck[1]
            

            store=[]
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zip if zip else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            
            store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
            print("====",str(store))
            return_main_object.append(store)  
    return return_main_object


           
    
def scrape():
    data = fetch_data()

    write_output(data)

scrape()
