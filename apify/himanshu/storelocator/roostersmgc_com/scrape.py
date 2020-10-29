# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
session = SgRequests()

def write_output(data):
    with open('roostersmgc_com.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.roostersmgc.com"
    soup = bs(session.get("https://www.roostersmgc.com/book-appointment.html").text, "lxml")

    for state_link in soup.find("div",{"class":"state-buttons"}).find_all("a"):
        
        state_soup = bs(session.get(state_link['href']).text, "lxml")

        if state_soup.find("table"):
            for url in state_soup.find("table").find_all("a"):
                
                page_url = base_url + url['href']

                location_soup = bs(session.get(page_url).text, "lxml")
            
                location_name = url.text.split(",")[0].strip()
                street_address = location_soup.find("span",{"itemprop":"streetAddress"}).text.strip()
                city = location_soup.find("span",{"itemprop":"addressLocality"}).text.strip()
                state = location_soup.find("span",{"itemprop":"addressRegion"}).text.strip()
                zipp = location_soup.find("span",{"itemprop":"postalCode"}).text.strip()
                phone = location_soup.find("span",{"itemprop":"telephone"}).text.strip()
                coords = location_soup.find(lambda tag : (tag.name == "script") and "salonDetailLat" in tag.text).text
                
                store_number = coords.split("salonDetailSalonID =")[1].split(";")[0].replace('"',"")
                lat = coords.split("salonDetailLat =")[1].split(";")[0].replace('"',"")
                lng = coords.split("salonDetailLng =")[1].split(";")[0].replace('"',"")
                hours = " ".join(list(location_soup.find("div",{"class":"salon-timings"}).stripped_strings)).replace("Hours:","")

                
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append(store_number) 
                store.append(phone)
                store.append("Salon")
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
