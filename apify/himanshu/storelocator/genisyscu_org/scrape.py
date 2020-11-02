import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = locator_domain = "https://www.genisyscu.org"
    country_code = "US"
    store_number = "<MISSING>"
    r = session.get("https://www.genisyscu.org/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    address = []
    for location in soup.find("section",{'class':"inside"}).find_all('ul'):
        for li in location.find_all('li'):
            if li.find("a")!= None:
                data_new =  (li.find("a")['href'])
                page_url= base_url + data_new
                location_name = li.find("a").text.strip()
                location_type = "Genisys Branch"
                r1 = session.get(page_url,headers=headers)
                soup1 = BeautifulSoup(r1.text,"lxml")
                try:
                    location_name = soup1.find("h1").text.replace("Genisys Credit Union - ","")
                    address = soup1.find('p',{'class':'largesub'})
                    city = (address.text.split("<br />")[0].split("\r\n")[-1].split(",")[0])
                    zipp = (address.text.split("<br />")[0].split("\r\n")[-1].split(",")[1].split(" ")[-1])
                    state = (address.text.split("<br />")[0].split("\r\n")[-1].split(",")[1].split(" ")[1])
                    street_address = " ".join(address.text.split("<br />")[0].split("\r\n")[:-1]).replace(",","").replace(".","")
                    phone1 = soup1.find_all('p',{'class':'largesub'})[1]
                    phone = (phone1.text.split("<br />")[0].split("\r\n")[0].replace("Call: ","").replace("Call or Text: ",""))
                    data8 = (soup1.find_all("p")[-6].find("iframe")['src'].split("!2d")[1].split("!2m")[0].split("!3d"))
                    latitude = data8[1].split("!3m")[0]
                    longitude = data8[0]
                    hours_of_operation = (" ".join(soup1.find('div',{'class':'column col-100'}).text.split(" ")[0:]).replace("\n","")).replace("Hours","Hours ").replace("PM","PM ") 
                except:
                    city = "<MISSING>"
                    zipp = "<MISSING>"
                    state = "<MISSING>"
                    street_address = "<MISSING>"
                    phone = "800-521-8440"
                    location_name = "Grand Rapids Area"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                store = []
                store.append(base_url if base_url else "<MISSING>")
                store.append(location_name if location_name else "<MISSING>") 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append("<MISSING>") 
                store.append(phone if phone else "<MISSING>")
                store.append(location_type if location_type else "<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation.replace('Branch Hours ','') if hours_of_operation else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")
                # if store[2] in address :
                #     continue
                # address.append(store[2])
                yield store 
    r1 = session.get("https://www.genisyscu.org/atmbranch-locator?street=&search=&state=&radius=50&options%5B%5D=atms#",headers=headers)
    soup1 = BeautifulSoup(r1.text,"lxml")
    data7 = (soup1.find_all("div",{"class":"loc_list"}))
    for i in data7:
        data8 = (i.find_all("div",{"class":"listbox"}))
        for j in data8:
            data9 = (j.find_all("p")[-1])
            street_address = str(data9).split("<br/>")[0].replace('<p>',"").replace(".","").replace("Points Dr","Point Dr")
            state = data9.text.split(",")[1].split(" ")[1]
            zipp = data9.text.split(",")[1].split(" ")[-1]
            city = str(data9).split("<br/>")[1].split(",")[0]
            location_name = j.find("a").text.strip()
            phone = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"
            page_url = "https://www.genisyscu.org/atmbranch-locator?street=&search=&state=&radius=50&options%5B%5D=atms#"
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("ATM Location")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            yield store 
          
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
