import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://local.fuel.safeway.com/"

    
    headers = {           
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    
    }
    r = session.get("https://local.fuel.safeway.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find_all("a",{"class":"Directory-listLink"}):
        
        if link['data-count'] == "(1)":
            page_url = "https://local.fuel.safeway.com/" + link['href']
            
            location_r = session.get(page_url, headers=headers)
            location_soup = BeautifulSoup(location_r.text, "lxml")
            location_name = location_soup.find("h1",{"class":"ContentBanner-h1"}).text
            street_address = location_soup.find("span",{"class":"c-address-street-1"}).text
            city = location_soup.find("span",{"class":"c-address-city"}).text
            state = location_soup.find("abbr",{"class":"c-address-state"}).text
            zipp = location_soup.find("span",{"class":"c-address-postal-code"}).text
            phone = location_soup.find("div",{"class":"Phone-display Phone-display--withLink"}).text.strip()
            hours = " ".join(list(location_soup.find("table",{"class":"c-hours-details"}).find("tbody").stripped_strings))
            latitude = location_soup.find("meta",{"itemprop":"latitude"})['content']
            longitude = location_soup.find("meta",{"itemprop":"longitude"})['content']
            location_type = "Fuel"
            country_code = "US"
            
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone )
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            yield store
        
        else:

            state_link = "https://local.fuel.safeway.com/"+link['href']
            state_r = session.get(state_link, headers=headers)
            state_soup = BeautifulSoup(state_r.text, "lxml")
            for city_link in state_soup.find_all("a",{"class":"Directory-listLink"}):

                if city_link['data-count'] == "(1)":
                    
                    page_url = "https://local.fuel.safeway.com/"+city_link['href']
                    location_r = session.get(page_url, headers=headers)
                    location_soup = BeautifulSoup(location_r.text, "lxml")
                    location_name = location_soup.find("h1",{"class":"ContentBanner-h1"}).text
                    street_address = location_soup.find("span",{"class":"c-address-street-1"}).text
                    city = location_soup.find("span",{"class":"c-address-city"}).text
                    state = location_soup.find("abbr",{"class":"c-address-state"}).text
                    zipp = location_soup.find("span",{"class":"c-address-postal-code"}).text
                    phone = location_soup.find("div",{"class":"Phone-display Phone-display--withLink"}).text.strip()
                    hours = " ".join(list(location_soup.find("table",{"class":"c-hours-details"}).find("tbody").stripped_strings))
                    latitude = location_soup.find("meta",{"itemprop":"latitude"})['content']
                    longitude = location_soup.find("meta",{"itemprop":"longitude"})['content']
                    location_type = "Fuel"
                    country_code = "US"
                    
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append(country_code)
                    store.append("<MISSING>")
                    store.append(phone )
                    store.append(location_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours)
                    store.append(page_url)
                    yield store
                    
    
                else:

                    r6 = session.get("https://local.fuel.safeway.com/"+city_link['href'], headers=headers)
                    soup6 = BeautifulSoup(r6.text, "lxml")
        
                    for lastlink in soup6.find_all("a",{"class":"Teaser-titleLink"}):
                        page_url = lastlink['href'].replace("../","https://local.fuel.safeway.com/")
                        location_r = session.get(page_url, headers=headers)
                        location_soup = BeautifulSoup(location_r.text, "lxml")
                        location_name = location_soup.find("h1",{"class":"ContentBanner-h1"}).text
                        street_address = location_soup.find("span",{"class":"c-address-street-1"}).text
                        city = location_soup.find("span",{"class":"c-address-city"}).text
                        state = location_soup.find("abbr",{"class":"c-address-state"}).text
                        zipp = location_soup.find("span",{"class":"c-address-postal-code"}).text
                        phone = location_soup.find("div",{"class":"Phone-display Phone-display--withLink"}).text.strip()
                        hours = " ".join(list(location_soup.find("table",{"class":"c-hours-details"}).find("tbody").stripped_strings))
                        latitude = location_soup.find("meta",{"itemprop":"latitude"})['content']
                        longitude = location_soup.find("meta",{"itemprop":"longitude"})['content']
                        location_type = "Fuel"
                        country_code = "US"
                        
                        store = []
                        store.append(base_url)
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(zipp)
                        store.append(country_code)
                        store.append("<MISSING>")
                        store.append(phone )
                        store.append(location_type)
                        store.append(latitude)
                        store.append(longitude)
                        store.append(hours)
                        store.append(page_url)
                        yield store
                

       
        
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
