import csv
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import json
session = SgRequests()

base_url = 'https://eurekarestaurantgroup.com'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    soup = BeautifulSoup(session.get("https://eurekarestaurantgroup.com/locations").text,"lxml")
    for url in soup.find("section",{"id":"content"}).find_all("a"):
        page_url = url['href']

        location_soup = BeautifulSoup(session.get(page_url).text, "lxml")
        addr = list(location_soup.find("div",{"class":"col-sm-3 padding-0"}).find("p").stripped_strings)

        street_address = addr[0]
        city = addr[1].split(",")[0]
        state = addr[1].split(",")[-1].split()[0]
        zipp = addr[1].split(",")[-1].split()[-1]
        
        if "@" not in addr[-1]:
            phone = addr[-1]
        else:
            phone = "<MISSING>"

        hours = re.sub(r'\s+'," "," ".join(list(location_soup.find_all("div",{"class":"col-sm-3"})[1].stripped_strings)).replace("Restaurant Hours:","")).strip()
        
        
    
        output = []
        output.append(base_url) # url
        output.append('<MISSING>') #location name
        output.append(street_address) #address
        output.append(city) #city
        output.append(state) #state
        output.append(zipp) #zipcode
        output.append("US") #country code
        output.append("<MISSING>") #store_number
        output.append(phone) #phone
        output.append("Restaurants") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(hours) #opening hours
        output.append(page_url)
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
