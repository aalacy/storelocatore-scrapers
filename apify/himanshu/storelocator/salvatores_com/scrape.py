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
    
    base_url = "https://www.salvatores.com/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]
    k= soup.find_all('div',{'class':"all-locations"})
    list1=[]
    main_hours=[]
    for i in k:
        data =i.find_all("div",{"class":"address"})
        phone1 = i.find_all('div',{"class":"phone"})
        names= i.find_all('h3')

        for link in names:
            time = ''
            r = session.get(link.a['href'])
            min_soup= BeautifulSoup(r.text,"lxml")
            hours = min_soup.find("div",{"class":"location-hours"})
            h1 = list(hours.stripped_strings)
            for h in h1:
                if "Location Hours:" in h:
                    pass
                else:
                    time = time + ' ' +h
            main_hours.append(time)
        
        for n in names:
            store_name.append(list(n.stripped_strings))

        for p in phone1:
            list1.append(list(p.stripped_strings))

        
        for index,j in enumerate(data):
            tem_var =[]
            street_address = list(j.stripped_strings)[0]
            city = list(j.stripped_strings)[1].split(',')[0]
            state  = list(j.stripped_strings)[1].split(',')[1].split( )[0]
            zipcode = list(j.stripped_strings)[1].split(',')[1].split( )[1]
            phone=list1[index][0]
            hours_of_operation = main_hours[index]
            
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("salvatores")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours_of_operation)
            store_detail.append(tem_var)
            
            
    
    
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.salvatores.com")
        store.append(store_name[i][0])
        store.extend(store_detail[i])
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
