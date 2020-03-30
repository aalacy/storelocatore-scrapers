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
    writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code","store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
    # Body
    for row in data:
        writer.writerow(row)
def fetch_data():
    base_url = "https://theoriginalpizzaking.com/locations"
    r = session.get(base_url)
    store_name = []
    soup = BeautifulSoup(r.content,"lxml")
    return_main_object =[]
    store_detail =[]
    
    k = soup.find_all("figcaption")
    for i in k:
        data1=''
        temp= []
        spans = i.find_all("p")
        new_list =[]
        for j in spans:
            temp_var=[]
            data = (list(j.stripped_strings))
            if len(data)==1:
                temp.append(data[0])
            else:
                name = data[0]
                store_name.append(name)
                street_address = data[1]
                city = data[2].split(',')[0]
                state = data[2].split(',')[1].split( )[0]
                zipcode = data[2].split(',')[1].split( )[1]
                phone = data[3]
                temp_var.append(street_address)
                temp_var.append(city)
                temp_var.append(state)
                temp_var.append(zipcode)
                temp_var.append("US")
                temp_var.append("<MISSING>")
                temp_var.append(phone)
                temp_var.append("theoriginalpizzaking")
                temp_var.append("<MISSING>")
                temp_var.append("<MISSING>")
                temp_var.append("<MISSING>")
            
            if temp_var != []:
                store_detail.append(temp_var)
      
        if temp != []:
            name = temp[0]
            store_name.append(name)
            street_address = temp[1]
            city =  temp[2].split(',')[0]
            state = temp[2].split(',')[1].split( )[0]
            zipcode = temp[2].split(',')[1].split( )[1]
            phone = temp[3]
            new_list.append(street_address)
            new_list.append(city)
            new_list.append(state)
            new_list.append(zipcode)
            new_list.append("US")
            new_list.append("<MISSING>")
            new_list.append(phone)
            new_list.append("theoriginalpizzaking")
            new_list.append("<MISSING>")
            new_list.append("<MISSING>")
            new_list.append("<MISSING>")
            store_detail.append(new_list)
            
    for i in range(len(store_name)):
        store = list()
        store.append("https://theoriginalpizzaking.com")   
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)         
    print(return_main_object)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

