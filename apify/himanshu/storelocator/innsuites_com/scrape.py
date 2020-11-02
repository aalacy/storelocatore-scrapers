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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://www.innsuites.com"
    
    r = session.get(base_url ,headers = header)
    soup = BeautifulSoup(r.text,"html.parser")
    
    for val in soup.find('ul',{'class':'wrap'}).ul.find_all('a'):
            link = val['href']
            r = session.get(link ,headers = header)
            soup = BeautifulSoup(r.text,"html.parser")
            locator_domain = base_url
            vk = soup.find('section',{'id':'description'})
            location_name = vk.find('h2').text.strip()
            de = vk.find('b').text.strip()
            if len(de.split('•')) == 2:
                if de.split('•')[0] != "":
                    street_address = de.split('•')[0].strip()
                    city = de.split('•')[1].split(',')[0].strip()
                    state  = de.split('•')[1].split(',')[1].strip().split(' ')[0].strip()
                    zip  = de.split('•')[1].split(',')[1].strip().split(' ')[1].strip()
                    phone = de.split('•')[1].split(',')[1].strip().split(' ')[-1].strip()
                   
                else:
                    street_address = '2400 Yale Boulevard SE'
                    
                    city = de.strip().split('•')[1].split(',')[0].strip()
                    state = de.strip().split('•')[1].split(',')[1].strip().split(' ')[0].strip()
                    zip  = de.strip().split('•')[1].split(',')[1].strip().split(' ')[1].strip()
                    phone = de.split('•')[1].split(',')[1].strip().split(' ')[-1].strip()
                    
                    
            else:

                    if len(de.split(',')) == 3:
                        street_address = de.split(',')[0].strip()
                        
                        city = de.split(',')[1].split(',')[0].strip()
                    
                        state  = de.split(',')[2].strip().split(' ')[0].strip()
                    
                        zip  = de.split(',')[2].strip().split(' ')[1].strip()
                    
                        phone = de.split(',')[2].strip().split(' ')[-1].strip()
                    else:

                        street_address = de.split(',')[0].strip()
                        
                        city = de.split(',')[2].strip()
                    
                        state  = '<MISSING>'
                    
                        zip  = '<MISSING>'
                    
                        phone = de.split(',')[3].strip().split(' ')[-1].strip()
                        


            if "Route 66" in street_address:
                city = "Flagstaff"
                state = "Arizona"
            store_number = '<MISSING>'
            country_code = 'US'
            location_type = '<MISSING>'
            latitude = soup.find(class_="hotel_latlong")["value"].split(",")[0]
            longitude = soup.find(class_="hotel_latlong")["value"].split(",")[1]
            hours_of_operation = '<MISSING>'

            store=[]
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(link)
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
