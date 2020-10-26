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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    base_url = "https://www.osfhealthcare.org"
    addressess=[]
    r = session.get("https://www.osfhealthcare.org/practices/search/")
    soup = BeautifulSoup(r.text, "lxml")
    for data in soup.find_all("div",{"class":"nav-box"}):
        for url in data.find_all("a"):
            loc_type = url.text

            r1 = session.get(base_url+url['href'])
            soup1 = BeautifulSoup(r1.text, "lxml")

            for link in soup1.find_all("a",{"itemprop":"url"}):
                page_url = base_url+link['href']

                location_r = session.get(page_url)
                location_soup = BeautifulSoup(location_r.text, "lxml")
                location_name = location_soup.find("h2",{"itemprop":"name"}).text
                street_address = list(location_soup.find("span",{"itemprop":"streetAddress"}).stripped_strings)[0]
                city = location_soup.find("span",{"itemprop":"addressLocality"}).text
                state = location_soup.find("span",{"itemprop":"addressRegion"}).text
                try:
                    zipp = location_soup.find("span",{"itemprop":"postalCode"}).text
                except:
                    zipp='<MISSING>'
                store_number = page_url.split("/")[-2]
                try:
                    phone = location_soup.find("span",{"itemprop":"telephone"}).text.split("x")[0].strip()
                except:
                    phone = "<MISSING>"
                location_type = loc_type
                
                try:
                    coord = location_soup.find("div",{"id":"practice-buttons"}).find_all("a",{"class":"callout-button"})
                    for maps in coord:
                        if "google.com/maps" in maps['href']:
                            if "/@" in maps['href']:
                                latitude = maps['href'].split("@")[1].split(",")[0]
                                longitude = maps['href'].split("@")[1].split(",")[1]
                            elif "ll=" in maps['href']:
                                latitude = maps['href'].split("ll=")[1].split(",")[0]
                                longitude = maps['href'].split("ll=")[1].split(",")[1].split("&")[0]
                            else:
                                latitude = "<MISSING>"
                                longitude = "<MISSING>"
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

                if location_soup.find("span",{"class":"practice-always-open"}):
                    hours = " ".join(list(location_soup.find_all("span",{"class":"practice-always-open"})[-1].stripped_strings))
                elif location_soup.find("table",{"class":"practice-weekly-hours nostack"}):
                    hours = " ".join(list(location_soup.find_all("table",{"class":"practice-weekly-hours nostack"})[-1].stripped_strings))
                elif location_soup.find("span",{"class":"practice-appointment-only"}):
                    hours = " ".join(list(location_soup.find_all("span",{"class":"practice-appointment-only"})[-1].stripped_strings))
                else:
                    hours = "<MISSING>"
                
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
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append(hours)
                store.append(page_url)
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                if str(store[2]+store[-5]) in addressess:
                    continue
                addressess.append(str(store[2]+store[-5]))
                # print("data == "+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                yield store
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
