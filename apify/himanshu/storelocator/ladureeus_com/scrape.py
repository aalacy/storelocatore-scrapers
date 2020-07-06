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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.laduree.us"
    r = session.get("https://www.laduree.us/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    location_url = []
    hours= []
    for location in soup.find_all("div",{"class":"sqs-block html-block sqs-block-html"})[1:10]:
        hours.append( str(list(location.stripped_strings)).split("Opening hours:")[-1].replace("'","").replace("]","").replace(",","").strip().replace("pm Fri","pm, Fri"))
    ind=0
    for location in soup.find("div",{"id":"content"}).find_all("div",{"class":"sqs-block-content"}):
        if not location.find("h3"):
            continue
        name = " ".join(list(location.find("h3").stripped_strings))
        if "coming soon" in name:
            continue
        address = " ".join(list(location.find("p").stripped_strings)).replace("USA","").replace('       '," ").replace("Manhasset, New York For more information email us at ladureeus@laduree.com","<MISSING>").replace("Street - ","Street").strip()
        store_zip_split = re.findall("([0-9]{5})",address)
        if store_zip_split:
            store_zip = store_zip_split[0]
        state_split = re.findall("- ([A-Z]{2}) ",address)
        if state_split:
            state = state_split[0]
        else:
            state = "<MISSING>"
        street_address = address.split(store_zip)[0]
        city = address.split(store_zip)[-1].replace(state,"").replace("-","").replace(' ',"")
        if location.find("p",text=re.compile(".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?")):
            phone = location.find("p",text=re.compile(".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?")).text
        hours_tag = location.find(text=re.compile("hours"))
        if "HIRSHLEIFERS" in name:
            continue
        store = []
        store.append("https://www.laduree.us")
        store.append(name.replace("É","E").replace("é","e"))
        store.append(street_address.strip())
        store.append(city)
        store.append(state)
        store.append(store_zip if store_zip else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("laduree")
        store.append("<MISSING>")
        store.append("<MISSING>")
        try:
            if "temporarily" in hours[ind] or "Temporarily" in hours[ind] :
                store.append("<MISSING>")
            else:
                store.append(hours[ind])
        except:
            store.append("<MISSING>")
        store.append("https://www.laduree.us/locations")
        
        yield store
        ind=ind+1
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
