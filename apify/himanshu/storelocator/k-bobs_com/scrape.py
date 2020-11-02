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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
  
    base_url= "https://www.k-bobs.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    data = soup.find_all("div",{"class":"fw-text-inner"})
    hours = []
    name_store=[]
    store_detail=[]
    phone=[]
    return_main_object=[]
    names = soup.find_all("h6")
    for n in names:
       if "Follow Us On" in n.text.replace("\n",""):
            pass
       else:
            name_store.append(n.text.replace("\n",""))
    
    for i in data:
        tem_var =[]
        if i.find("p").a:
            pass
        else:
            hours.append(i.find("p").text)

        if len(list(i.stripped_strings))==4:
            if "Sun–Sat:" in list(i.stripped_strings) or "Sat–Sun:" in list(i.stripped_strings):
                pass
            else:
                street_address = list(i.stripped_strings)[0]
                city = list(i.stripped_strings)[1].split(',')[0]
                state  = list(i.stripped_strings)[1].split(',')[1].split( )[0]
                zipcode = list(i.stripped_strings)[1].split(',')[1].split( )[1]
                phone.append(list(i.stripped_strings)[3])
                
                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode)
                store_detail.append(tem_var)
    
    for i in range(len(name_store)):
        store = list()
        store.append("https://www.k-bobs.com")
        store.append(name_store[i])
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[i])
        store.append("k-bobs")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours[i])
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
