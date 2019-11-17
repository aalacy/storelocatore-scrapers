import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
 
def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://thegrandtheatre.com"
    return_main_object=[]
    r = requests.get(base_url+'/search?type=locations',headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',{"id":"searchresults"}).find_all('a',{"class":"searchtitle"})
    for i in main:
        link = base_url+'/'+i['href']
        r1 = requests.get(link,headers=headers)
        nonBreakSpace = '&nbsp;'
        soup1=BeautifulSoup(r1.text,'lxml')
        location_name=soup1.find('div',{"id":"theatre"}).find('div',{"class":"title"}).text.strip()
        st=list(soup1.find('div',{"id":"theatre"}).find('div',{"class":"small"}).stripped_strings)
        lat_tmp = soup1.find('div',{"id":"map"}).find('iframe')['src'].split('m&ll=')[1].split('&spn=0.')[0].split(',')
        lat =lat_tmp[0]
        lng = lat_tmp[1]
        # print(lng)
        
        if (len(st)==2):
            address_tmp= st[0].split('|')
            address =address_tmp[0]
            city_tmp = address_tmp[1].strip().split(',')
            city = city_tmp[0]
            state_tmp = city_tmp[1].strip().split('\xa0')
            state = state_tmp[0]
            zip = state_tmp[1]
            phone = st[-1].replace('Information:','').strip()
             
            
        else:
            address_tmp = st[1].split('|')
            address = address_tmp[0]
            city_tmp = address_tmp[1].strip().split(',')
            city = city_tmp[0]
            state_tmp = city_tmp[1].strip().split('\xa0')
            state = state_tmp[0]
            zip = state_tmp[1]
            phone = st[-1].replace('Information:','').strip()
            
        
        country="US"
        hour=''
        store_number=''
        store=[]
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>")
        store.append(address.encode('ascii', 'ignore').decode('ascii').strip() if address else "<MISSING>")
        store.append(city.encode('ascii', 'ignore').decode('ascii').strip() if city else "<MISSING>")
        store.append(state.encode('ascii', 'ignore').decode('ascii').strip() if state else "<MISSING>")
        store.append(zip.encode('ascii', 'ignore').decode('ascii').strip() if zip else "<MISSING>")
        store.append(country.encode('ascii', 'ignore').decode('ascii').strip() if country else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(lat.encode('ascii', 'ignore').decode('ascii').strip() if lat else "<MISSING>")
        store.append(lng.encode('ascii', 'ignore').decode('ascii').strip() if lng else "<MISSING>")
        store.append(hour.encode('ascii', 'ignore').decode('ascii').strip() if hour else "<MISSING>")
        store.append(link.encode('ascii', 'ignore').decode('ascii').strip())
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
