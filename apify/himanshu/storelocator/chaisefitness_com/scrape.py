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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://chaisefitness.com"
  
    soup = BeautifulSoup(session.get(base_url).text ,"lxml")
    

    for ltag in soup.find('ul',{"class":"versions"}).find_all('li',{"class":re.compile("item")}):
        soup1 = BeautifulSoup(session.get(ltag.find('a')['href']).text ,"lxml")
        page_url = soup1.find('a',text=re.compile("Location"))['href']
        soup2 = BeautifulSoup(session.get(page_url).text ,"lxml")
        
        location_name = soup2.find("h1",{"class":"white mega"}).text
        
        street_address = soup2.find("strong",{"class":"white"}).text
        place = soup2.find_all("strong",{"class":"white"})[-1].text
        city = place.split(",")[0]
        state = place.split(",")[1].split()[0]
        zipp = place.split(",")[1].split()[1]
        
        phone = soup2.find("span",{"class":"white"}).text.split("maplewood@")[0].replace("."," ").strip()
        
        coordinates = soup2.find('a',text="Get Directions")['href'].split('@')[1].split(',')
        lat = coordinates[0]
        lng = coordinates[1]
        
        store=[]
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("chaisefitness")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
