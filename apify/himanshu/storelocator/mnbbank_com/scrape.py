import csv
import requests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://mnbbank.com/"
    locator_domain = "https://mnbbank.com/"
    loacation_url = base_url+'locations/'
    r = requests.get(loacation_url,headers = header)
    soup = BeautifulSoup(r.text,"lxml")


    for script in soup.find_all(
                lambda tag: (tag.name == "script") and "console.log" in tag.text):
        latitude = script.text.split('(')[1].split(')')[0].split(',')[0]
        longitude= script.text.split('(')[1].split(')')[0].split(',')[-1]
        # print(script.text.split("'")[1])
        # print('~~~~~~~~~~~~~~~~~~~~~~~')
        loc_list = BeautifulSoup(script.text.split("'")[1],'lxml')
        # print(loc_list.prettify())
        if loc_list.h5 is not None:
            phone = loc_list.h5.text.replace('Phone: ','').encode('ascii', 'ignore').decode('ascii').strip()
        else:
            phone = "<MISSING>"

        address_list = list(loc_list.h4.stripped_strings)
        # print(address_list)
        # print(len(address_list))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')

        state= address_list[0].split(',')[-1].split()[0].strip()
        zipp = address_list[0].split(',')[-1].split()[-1].strip()
        street_address  = address_list[0].split(',')[0].encode('ascii', 'ignore').decode('ascii').strip()
        if  "Line Rd" not in " ".join(address_list[0].split(',')[0].split()[-2:]) :
            city = " ".join(address_list[0].split(',')[0].split()[-2:]).replace('5','').replace('Street','').replace('Road','').replace('Main Street','').replace('Bluff Street','').replace('King Blvd','').replace('Oak Street','').replace('1025 Markham','').replace('Parkway','').replace('.','').replace('102 Markham','').strip()
        else:
            city = "<MISSING>"
        location_name = city
        hours_of_operation = loc_list.find_all('p')
        fk = []
        for gg in hours_of_operation:
            fk.append(gg.text.replace('ATM Available',''))

        hours_of_operation = ' '.join(list(fk)).strip()
        page_url ="<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        store=[]
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if latitude else '<MISSING>')
        store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
        store.append(page_url  if page_url else '<MISSING>')
        # print(str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
