import csv
import requests
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    
    bank_locations_url = 'https://banks.amerisbank.com/'

    for bank_state_link in BeautifulSoup(session.get(bank_locations_url).content, 'lxml').find_all("a",{"linktrack":re.compile("State index page")}):
        
        for bank_city_link in BeautifulSoup(session.get(bank_state_link.get('href')).content, 'lxml').find_all("a",{"dta-linktrack":re.compile("City index page -")}):

            for branch_link in BeautifulSoup(session.get(bank_city_link.get('href')).content, 'lxml').find_all("a",{"linktrack":"Landing page"}):
                page_url = branch_link.get('href')
                soup = BeautifulSoup(session.get(page_url).content, 'lxml')
                
                json_data = json.loads(soup.find(lambda tag:(tag.name == "script") and '"streetAddress"' in tag.text).text.replace("//if applied, use the tmpl_var to retrieve the database value",""))
                
                location_name = soup.find("div",{"id":"branchName"}).text.strip()
                street_address = json_data['address']['streetAddress']
                city = json_data['address']['addressLocality']
                state = json_data['address']['addressRegion']
                zipp = json_data['address']['postalCode']    
                country_code = json_data['address']['addressCountry']
                store_number = json_data['@id']
                if json_data['telephone']:
                    phone = json_data['telephone']
                else:
                    phone = "866.616.6020"
                location_type = json_data['@type']
                lat = json_data['geo']['latitude']
                lng = json_data['geo']['longitude']

                hours = "Branch Hours "+ " ".join(list(soup.find("table",{"id":"hoursTable"}).stripped_strings))
                if soup.find("p",{"id":"driveDesc"}):
                    hours = hours
                else:
                    hours+= " Drive-Thru Hours "+" ".join(list(soup.find("table",{"id":"hoursTableDT"}).stripped_strings))
                if "n/a" in hours or "N/A" in hours:
                    hours = "<MISSING>"
                store = []
                store.append("https://www.amerisbank.com/")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)   
                store.append(country_code)
                store.append(store_number if store_number.isdigit() else "<MISSING>")
                store.append(phone)
                store.append(location_type)
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])     
            
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store
                
                

    

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
