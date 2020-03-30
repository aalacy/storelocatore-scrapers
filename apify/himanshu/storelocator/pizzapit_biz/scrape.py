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
  
    base_url= "https://pizzapit.biz/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    data = soup.find_all("div",{"class":"fl-rich-text"})

    phone =[]
    street_address=[]
    name_store=[]
    store_detail=[]
    return_main_object=[]

    base_url1= "https://pizzapit.biz/locations/wi-madison-south-fitchburg/"
    r = session.get(base_url1)
    soup1= BeautifulSoup(r.text,"lxml")
    tem_var1=[]
    name1 =[]
    
    phone1 = list(soup1.find("tbody").p.stripped_strings)[1]
    street_address1 = list(soup1.find("tbody").p.stripped_strings)[2]
    city=list(soup1.find("tbody").p.stripped_strings)[3].split( )[0]
    state= list(soup1.find("tbody").p.stripped_strings)[3].split( )[1]
    
    tem_var1.append("https://pizzapit.biz")
    tem_var1.append(list(soup1.find("tbody").p.stripped_strings)[0])
    tem_var1.append(street_address1)
    tem_var1.append(city)
    tem_var1.append(state)
    tem_var1.append("<MISSING>")
    tem_var1.append("US")
    tem_var1.append("<MISSING>")
    tem_var1.append(phone1)
    tem_var1.append("pizzapit")
    tem_var1.append("<MISSING>")
    tem_var1.append("<MISSING>")
    tem_var1.append("<MISSING>")
   
    
    
    data = soup.find_all("div",{"class":"fl-rich-text"})
    for i in data:
        std = i.find_all('p')
        for st in std:
            if len(list(st.stripped_strings)) !=0:
                phone.append(list(st.stripped_strings)[1])

                street_address.append(list(st.stripped_strings)[2])
       
        name = i.find_all("strong")
        for n in name:
            if '  ' in n.text.replace("\n",""):
                pass
            else:
                name_store.append(n.text.replace("\n","")) 
                
    for i in range(len(name_store)):
        store = list()
        store.append("https://pizzapit.biz")
        store.append(name_store[i])
        store.append(street_address[i])
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[i])
        store.append("pizzapit")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    
    del return_main_object[6]
    return_main_object.insert(6,tem_var1)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
