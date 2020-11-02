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
    base_url = "https://www.centier.com/"
    location_url  = 'https://www.centier.com/includes/_ajax.php?action=getClosestLocations&filters=branch%2Catm%2Cez_deposit&lat=40.2671941&lng=-86.13490189999999'
    r = session.get(location_url ,headers = header).json()
    for idx, val in enumerate(r['locationDetails']):
        if idx > 0:
            if val != "":
                locator_domain = base_url
                soup = BeautifulSoup(val,"lxml")
                location_name = soup.find('span',{'class':'name'}).text
                

                street_address = list(soup.find('p',{'class':'basic-details'}).stripped_strings)[3]
                city = list(soup.find('p',{'class':'basic-details'}).stripped_strings)[4].split(',')[0]
                state = list(soup.find('p',{'class':'basic-details'}).stripped_strings)[4].split(',')[1].strip().split(' ')[0]
                zip = list(soup.find('p',{'class':'basic-details'}).stripped_strings)[4].split(',')[1].strip().split(' ')[1]
                country_code = 'USA'
                store_number = '<MISSING>'
                location_type = 'centier'
                latitude =  soup.find('div',{'class':'location-listing'})['data-lat']                
                longitude =  soup.find('div',{'class':'location-listing'})['data-lng']                
                phone = list(soup.find('p',{'class':'basic-details'}).stripped_strings)[2].replace('Phone:','').strip()
                dk = list(soup.find_all('p')[1].stripped_strings)
                
                if len(dk) > 2:
                    hours_of_operation = list(soup.find_all('p')[1].stripped_strings)[1] +','+list(soup.find_all('p')[1].stripped_strings)[2]
                else:
                    hours_of_operation = list(soup.find_all('p')[1].stripped_strings)[1]
                
               
               
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
