import csv
from bs4 import BeautifulSoup
import json
import re
from sgrequests import SgRequests

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

    base_url = "https://rockandreillys.com/"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    }

    soup = BeautifulSoup(session.get("https://rockandreillys.com/", headers=headers).text, "lxml")
    for url in soup.find("ul",{"class":"sub-menu elementor-nav-menu--dropdown"}).find_all("a"):
        page_url = url['href']
        
        
        # 
        # http://rockandreillysusc.com/
        location_soup = BeautifulSoup(session.get(page_url, headers=headers).text, "lxml")
        location_name = url.text
        
        if page_url == "http://www.rockandreillyslv.com/":
            
            addr = list(location_soup.find("div",{"class":"footer-txt"}).stripped_strings)
            street_address = addr[0]
            city = addr[1].split(",")[0]
            state = addr[1].split(",")[-1].split()[0]
            zipp = addr[1].split(",")[-1].split()[-1]

            hours = list(location_soup.find("div",{"class":"intro-txt-addy"}).stripped_strings)[-1]
            
            phone = location_soup.find_all("div",{"class":"footer-txt"})[1].text.strip()
            lat = "<MISSING>"
            lng = "<MISSING>"

        elif page_url == "http://rockandreillys.com/":


            addr = list(location_soup.find_all("div",{"class":"elementor-text-editor elementor-clearfix"})[-2].stripped_strings)
            street_address = addr[1]
            city = addr[2].split(",")[0]
            state = addr[2].split(",")[-1].split()[0]
            zipp = addr[2].split(",")[-1].split()[-1]
            phone = addr[-1]

            hours = location_soup.find_all("div",{"class":"elementor-text-editor elementor-clearfix"})[-1].text.strip().split("var")[0].replace("Hours:","").strip()
            lat = "<MISSING>"
            lng = "<MISSING>"
        else:
            location_soup = BeautifulSoup(session.get("https://www.rockandreillysusc.com/location/Rock-n-Reillys-USC/", headers=headers).text, "lxml")

            addr = list(location_soup.find("a",{"data-bb-track-category":"Address"}).stripped_strings)
            street_address = addr[0]
            city = addr[1].split(",")[0]
            state = addr[1].split(",")[-1].split()[0]
            zipp = addr[1].split(",")[-1].split()[-1]
            phone = location_soup.find("a",{"data-bb-track-category":"Phone Number"}).text.strip()

            coords = location_soup.find("a",{"data-bb-track-label":"Google+, Footer"})['href']
            lat = coords.split("@")[1].split(",")[0]
            lng = coords.split("@")[1].split(",")[1]
            
            hours = ''
            for hr in location_soup.find("section",{"id":"intro"}).find_all("p")[1:]:
               hours+= " "+ hr.text

        output = []
        output.append(base_url) # url
        output.append(location_name) #location name
        output.append(street_address) #address
        output.append(city) #city
        output.append(state) #state
        output.append(zipp) #zipcode
        output.append("US") #country code
        output.append("<MISSING>") #store_number
        output.append(phone) #phone
        output.append("Restaurants") #location type
        output.append(lat) #latitude
        output.append(lng) #longitude
        output.append(hours.strip()) #opening hours
        output.append(page_url)

        output = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in output]

        yield output





def scrape():
    data = fetch_data()
    write_output(data)

scrape()
