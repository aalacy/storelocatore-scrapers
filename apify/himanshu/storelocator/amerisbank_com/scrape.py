import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import html5lib
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
                soup = BeautifulSoup(session.get(page_url).content, 'html5lib')
                data = (soup.find_all("script",{"type":"application/ld+json"})[-1]).text
                data1 = (data.replace("//if applied, use the tmpl_var to retrieve the database value",""))
                
                json_data = json.loads(data1)
                
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
                try:
                    hours = " ".join(list(soup.find("div",{"class":"flexRight hideATMNo"}).stripped_strings))
                    
                except:
                    try:
                        hours = " ".join(list(soup.find("div",{"class":"flexRight hideATM"}).stripped_strings))
                    except:
                        hours = " ".join(list(soup.find("div",{"class":"flexRight"}).stripped_strings))
                if "n/a" in hours or "N/A" in hours:
                    hours = "<MISSING>"
                if "24 Hour Access" in hours:
                    location_type = "ATM's"
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
                store.append(location_type.replace("BankOrCreditUnion","Bank Or CreditUnion"))
                store.append(lat)
                store.append(lng)
                store.append(hours.replace("Drive-Thru Hours Monday: Drive-Thru Service Not Available Tuesday: Drive-Thru Service Not Available Wednesday: Drive-Thru Service Not Available Thursday: Drive-Thru Service Not Available Friday: Drive-Thru Service Not Available Saturday: Drive-Thru Service Not Available Sunday: Drive-Thru Service Not Available ","").replace("HOURS ","").replace(" Drive-Thru Hours",", Drive-Thru Hours").replace("Branch Lobby Hours ",""))
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
