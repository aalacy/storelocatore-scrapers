import csv
import requests
from bs4 import BeautifulSoup
import re
import json 

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
    base_url = "https://www.viaero.com"
    r = requests.get("https://info.viaero.com/store-directory")
    return_main_object = []
    addressess = []
    # try:
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find_all('a'):
        if 'Visit Store' in location.text:
            link = ('https://info.viaero.com'+location["href"]).replace('//info.viaero.comhttps:','').replace("//info.viaero.comhttps:",'')
            
            try:
                location_request = requests.get(link)
            except:
                pass

            location_soup = BeautifulSoup(location_request.text,"lxml")
            hour=' '.join((list(location_soup.find("table").stripped_strings)))
            location_script = location_soup.find("script",{"type":"application/ld+json"}).text.replace("}]\n},",'},')
            obj= json.loads(location_script)
            if 'latitude' in obj['geo']:
                latitude = obj['geo']['latitude']
            else:
                latitude = "<MISSING>"
            if 'longitude' in obj['geo']:
                longitude = obj['geo']['longitude'] 
            else:
                longitude = "<MISSING>"
            address = (obj['address']['streetAddress']).replace("504","405")
            location_type = obj['@type'] 
            city = obj['address']['addressLocality'] 
            state = obj['address']['addressRegion'] 
            zipp = obj['address']['postalCode'] 
            phone = obj['telephone']
            page_url = obj ['url'] 
            location_name = location_soup.find_all("div",{"class":"banner-content"})[-1].find("h1").text.split("—")[0].strip()
            store = []
            store.append("https://www.viaero.com")
            store.append(location_name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hour)
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store
    link = ("https://info.viaero.com/viaero-wireless-dealer-fort-morgan") 
    location_request = requests.get(link)
    location_soup = BeautifulSoup(location_request.text,"lxml")
    hour=' '.join((list(location_soup.find("table").stripped_strings)))
    location_script = location_soup.find("script",{"type":"application/ld+json"}).text.replace("}]\n},",'},')
    obj= json.loads(location_script)
    if 'latitude' in obj['geo']:
        latitude = obj['geo']['latitude']
    else:
        latitude = "<MISSING>"
    if 'longitude' in obj['geo']:
        longitude = obj['geo']['longitude'] 
    else:
        longitude = "<MISSING>"
    address = (obj['address']['streetAddress']).replace("504","405")
    location_type = obj['@type'] 
    city = obj['address']['addressLocality'] 
    state = obj['address']['addressRegion'] 
    zipp = obj['address']['postalCode'] 
    phone = obj['telephone']
    page_url = obj ['url'] 
    location_name = "Viaero Wireless - "+str(city)+","+str(state)  
    store = []
    store.append("https://www.viaero.com")
    store.append(location_name)
    store.append(address)
    store.append(city)
    store.append(state)
    store.append(zipp)
    store.append("US")
    store.append("<MISSING>")
    store.append(phone)
    store.append(location_type)
    store.append(latitude)
    store.append(longitude)
    store.append(hour)
    store.append(page_url)
    yield store
    link = ("https://info.viaero.com/viaero-wireless-brush") 
    location_request = requests.get(link)
    location_soup = BeautifulSoup(location_request.text,"lxml")
    data = location_soup.find("div",{"id":"hs_cos_wrapper_widget_19417560144"}).find("p")
    zipp = (data.text.split(" ")[-1])
    state = (data.text.split(" ")[-2])
    city = (data.text.split(" ")[-3].replace("StreetBrush,","Brush"))
    address = (" ".join(data.text.split(" ")[1:4]).split("Br")[0].split("ess")[1])
    mp = location_soup.find("span",{"id":"hs_cos_wrapper_widget_19417560145_"})
    hour = (" ".join(list(mp.stripped_strings)).replace("Store Hours ",""))
    phone = location_soup.find("div",{"id":"hs_cos_wrapper_widget_19417560144"}).find("a",{"href":"tel:+9708408113"}).text
    location_name = "Viaero Wireless - "+str(city)+","+str(state)
    # latitude = location_soup.find("iframe",{"class":"hs-responsive-embed-iframe"})
    latitude = "44.9115909864363"
    longitude = "-103.6257116843849"
    page_url = link  
    store = []
    store.append("https://www.viaero.com")
    store.append(location_name)
    store.append(address)
    store.append(city)
    store.append(state)
    store.append(zipp)
    store.append("US")
    store.append("<MISSING>")
    store.append(phone)
    store.append("MobilePhoneStore")
    store.append(latitude)
    store.append(longitude)
    store.append(hour)
    store.append(page_url)
    yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
