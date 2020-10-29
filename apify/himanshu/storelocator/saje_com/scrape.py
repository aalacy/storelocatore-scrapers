import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('saje_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                            "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)





def fetch_data():
    base_url = "https://www.saje.com/store-locator/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")

    for q in soup.find("div",{"class":"canada-stores"}).find_all("table",{"class":"store-locator-ca-table"}):
        location_name = q.find("td",{"class":"store-location-name"}).text
        # page_url = q.find("td",{"class":"store-location-name"})['href']
        phone = q.find("p",{"class":"phone-no"}).text
        full = list(q.find("td",{"class":"store-location-address"}).stripped_strings)[1].split(',')
        city = full[0]
        state = full[1]
        zipp = full[-1]
        street_address =  list(q.find("td",{"class":"store-location-address"}).stripped_strings)[0]
        page_url ="https://www.saje.com/"+q.find("td",{"class":"store-location-name"}).find("a")['href']
        r1 = requests.get(page_url)
        soup1= BeautifulSoup(r1.text,"lxml")
        lat=''
        log=''
        lats = str(soup1).split("var myLatlng = new google.maps.LatLng(")[-1].split(");")[0]
        if len(lats.split(",")) != 2:
            lat = "<MISSING>"
            log = "<MISSING>"
        else:
            lat = lats.split(",")[0]
            log = lats.split(",")[1]
        hours_of_operation = " ".join(list(soup1.find("div",{"class":"store-hours-main"}).stripped_strings)).replace("Holiday hours may vary",'').replace("Store Hours ",'')
    
        store = []
        if "1320 Trans-Canada Highway West" in street_address:
            lat = "<MISSING>"
            log = "<MISSING>" 
        store.append("https://www.saje.com/")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("CA")
        store.append("<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append( lat.replace("-80.9667","46.5"))
        store.append( log.replace("46.5","-80.9667"))
        store.append(hours_of_operation.replace('\n','').strip() if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        # logger.info("~~~~~~~~~~~~~~~~ ",store)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
    
    
    for q in soup.find("div",{"class":"us-stores"}).find_all("table",{"class":"store-locator-us-table"}):
        location_name = q.find("td",{"class":"store-location-name"}).text.replace("\n",'')
        # page_url = q.find("td",{"class":"store-location-name"})['href']
        lat=''
        log=''
        phone = q.find("p",{"class":"phone-no"}).text
        full = list(q.find("td",{"class":"store-location-address"}).stripped_strings)[1].split(',')
        city = full[0]
        state = full[1]
        zipp = full[-1]
        street_address =  list(q.find("td",{"class":"store-location-address"}).stripped_strings)[0]
        page_url ="https://www.saje.com/"+q.find("td",{"class":"store-location-name"}).find("a")['href']
        r1 = requests.get(page_url)
        soup1= BeautifulSoup(r1.text,"lxml")
        try:
            hours_of_operation = " ".join(list(soup1.find("div",{"class":"store-hours-main"}).stripped_strings)).replace("Holiday hours may vary",'').replace("Store Hours ",'')
        except:
            hours_of_operation="<MISSING>"


        soup1= BeautifulSoup(r1.text,"lxml")
        lats = str(soup1).split("var myLatlng = new google.maps.LatLng(")[-1].split(");")[0]
        if  len(lats.split(",")) != 2:
            lat = "<MISSING>"
            log = "<MISSING>"
        else:
            lat = lats.split(",")[0]
            log = lats.split(",")[1]
        store = []

        store.append("https://www.saje.com/")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append( lat.replace("-80.9667","46.5"))
        store.append( log.replace("46.5","-80.9667"))
        store.append(hours_of_operation.replace('\n','').strip() if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        # logger.info("~~~~~~~~~~~~~~~~ ",store)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        
        yield store

    
   

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


