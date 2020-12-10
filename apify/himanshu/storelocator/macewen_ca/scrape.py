
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import itertools as it
import datetime

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
    addresses = []
    # for i in it.chain(range(6764,20000)):
    for i in it.chain(range(1106,1117),range(1253,1328),range(1354,1365),range(1488,1519),range(1569,1672),range(2282,2284),range(2351,2353),range(2401,2409),range(2889,2891),range(2942,2945)):
        url = session.get("https://macewen.ca/?p="+str(i)).url
        
        url_data = ["retail/find-a-macewen",'commercial/cardlock-network/cardlock-locations','residential/locations']
        for i in url_data:
            
            if i in url:
               
                state=''
                zipp=''
                hours="<MISSING>"
                response = bs(session.get(url).text,"lxml")
                try:
                    street_address = response.find("div",class_="address").text.strip()
                except:
                    continue
                adr = " ".join(list(response.find("div",class_="contact").stripped_strings))
                location_name =str(response.find("div",class_="title").find("h2")).split("</span>")[-1].split("</h2>")[0].replace("amp;",' ')

                city = " ".join(list(response.find("div",class_="title").find("span",{"class":"eyebrow"}).stripped_strings))
                
                latitude = response.find("main",{'id':"main"}).find("div",{"id":"vue"}).find("single-place-map")[':lat']
                longitude = response.find("main",{'id':"main"}).find("div",{"id":"vue"}).find("single-place-map")[':lng']
                dayofweek = datetime.datetime.today().strftime("%A")
                hours = " ".join(list(response.find("div",class_="hours").stripped_strings)).replace("Open Hours","").replace("Today",dayofweek)
                phone_list = re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(adr))
                zip_list = list(response.find("div",class_="contact").stripped_strings)[2].split(",")[1].split(" ")
                if len(zip_list) == 4:
                    zipp = " ".join(zip_list[2:])
                else:
                    zipp = "<MISSING>"

                
                state_list = re.findall(r' ([A-Z]{2})', str(adr))
                if phone_list:
                    phone =  phone_list[-1]
                else:
                    phone = "<MISSING>"

                if state_list:
                    state = state_list[-1]

                page_url =url
                countryCode ="CA"
                store_number = "<MISSING>"
                store = []
                store.append("https://macewen.ca")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(countryCode)
                store.append(store_number)
                store.append(phone)
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours.split("** LCBO")[0].split("Currently Closed and ")[0])
                store.append(page_url)     
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
               
                yield store
            
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
