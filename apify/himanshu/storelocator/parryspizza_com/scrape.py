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
    base_url= "https://parryspizza.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    hours =[]
    phone =[]
    return_main_object=[]
    data = soup.find_all("div",{"class":"one-fourth locations-list md-float-left","vocab":"http://schema.org/","typeof":"LocalBusiness"})
    
    for d in data:
        names =d.find_all("b",{"property":"name"})
        st =d.find_all("div",{"property":"address","typeof":"PostalAddress"})
        
        for std in st:
            base_url1= std.a['href']
            r = session.get(base_url1)
            soup1= BeautifulSoup(r.text,"lxml")

            time = soup1.find_all("div",{"class":"entry-content","itemprop":"text"})
            for t in time:
                third =  t.find_all("div",{"class":"one-third"})
                for th in third:
                    if "Hours" in list(th.stripped_strings):
                        v= list(th.stripped_strings)
                        del v[0]
                        hours.append(" ".join(v))

        for std in st:
            tem_var =[]
            street_address=(list(std.stripped_strings)[2])
            phone.append(list(std.stripped_strings)[1])
            city = list(std.stripped_strings)[3]
            state = list(std.stripped_strings)[5]
            zipcode= list(std.stripped_strings)[6]
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            store_detail.append(tem_var)


        for n in names:
            store_name.append(n.text)
    

    for i in range(len(store_name)):
        store = list()
        store.append("https://parryspizza.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[i])
        store.append("parryspizza")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours[i])
        return_main_object.append(store)
  
        
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
