import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


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
    base_url = "https://www.thehickorytavern.com/"
    loacation_url = base_url+'locations/'
    r = session.get(loacation_url,headers = header)
    soup = BeautifulSoup(r.text,"lxml")

    get_link  = soup.find_all('li',{'class':'u-red'})
   
    for target_list in get_link:
        a = target_list.find('a')['href']
        
    

        r = session.get(a,headers = header)
        soup = BeautifulSoup(r.text,"lxml")
        da  = soup.find('div',{'class':'Callout-address'}).find('p').text.split(',')

        locator_domain = base_url
        location_name = soup.find('div',{'class':'Callout-header'}).find('h2').text
        city = da[0].split(' ')[-1]
        gk = da[1].strip().split(' ')
        state = gk[0]
        zip = gk[1]
        kb = da[0].split(' ')
        kb.pop(-1)
        street_address = ' '.join(kb)
        phone = soup.find('div',{'class':'Callout-number'}).find('span').text
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = 'thehickorytavern'
        latitude =  '<MISSING>'
        longitude =  '<MISSING>'
        kb =  list(soup.find('div',{'class':'Callout-times'}).stripped_strings)
        kb.pop(0)
        hours_of_operation = ' '.join(kb)
       
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
        return_main_object.append(store)  
    return return_main_object    
       
        
   
        
def scrape():
    data = fetch_data()    
    write_output(data)

scrape()
