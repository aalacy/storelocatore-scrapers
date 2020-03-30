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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',"Accept":"application/json, text/javascript, */*; q=0.01"
    }
    base_url= "http://ilovetaste.com/app/taste_melrose/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name =[]
    hours =[]
    k = soup.find_all("div",{"class":"side-widget below"})


    base_url1= "http://ilovetaste.com/app/taste_palisades/locations"
    r = session.get(base_url1)
    soup= BeautifulSoup(r.text,"lxml")
    k1 = soup.find_all("div",{"class":"side-widget below"})


    for i in  k1:
        tem_var =[]
        
        if  "Dinner" in list(i.stripped_strings):
            hours.append(" ".join(list(i.stripped_strings)).replace("Dinner",""))
        else:
            street_address = list(i.stripped_strings)[0].split(',')[0]
            city = list(i.stripped_strings)[0].split(',')[1]
            state = list(i.stripped_strings)[0].split(',')[2].split( )[0]
            zip1 = list(i.stripped_strings)[0].split(',')[2].split( )[1]
            phone  = list(i.stripped_strings)[-1].replace("Phone: ","")

            store_name.append(street_address)
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zip1.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("ilovetaste")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            
            store_detail.append(tem_var)
    


    for i in  k:
        tem_var =[]
        
        if  "Lunch" in list(i.stripped_strings):
            hours.append(" ".join(list(i.stripped_strings)))
        else:
            street_address = list(i.stripped_strings)[0].split(',')[0]
            city = list(i.stripped_strings)[0].split(',')[1]
            state = list(i.stripped_strings)[0].split(',')[2].split( )[0]
            zip1 = list(i.stripped_strings)[0].split(',')[2].split( )[1]
            phone  = list(i.stripped_strings)[-1].replace("Phone: ","")
        

            store_name.append(street_address)
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zip1.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("ilovetaste")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
           
            store_detail.append(tem_var)

    
    for i in range(len(store_name)):
        store = list()
        store.append("http://ilovetaste.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(hours[i])
     
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

