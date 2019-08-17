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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://www.thetinfishrestaurants.com/locations-menus/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    time =[]
    return_main_object=[]
    phone = []
    
    k= soup.find_all("table",{"border":"0","width":"90%","cellspacing":"0","cellpadding":"0"})
    k1= soup.find_all("h3",{"class":"style1"})

    for j in k1:
        store_name.append(j.text.split("|")[0])
        phone.append(j.text.split("|")[2].split("\n")[0])

    
    for i in  k:
        st = i.find_all("td",{"width":"31.37%"})
        hours = i.find_all("td",{"width":"24.93%"})

        for j in hours:
            time.append(" ".join(list(j.stripped_strings)).replace("( No Reservations ) We operate on a 1st come first serve basis.",""))
       
        for j in st:
            tem_var=[]
            zipcode =''
            p = j.find_all("p")
         
            if len(p[1].text.replace("\xa0","").split(','))==2:
                street_address=(j.p.text)
                
                city = p[1].text.replace("\xa0","").split(',')[0]
                state =  p[1].text.replace("\xa0","").split(',')[1].split( )[0]
                zipcode = p[1].text.replace("\xa0","").split(',')[1].split( )[1]

                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append(zipcode)
                store_detail.append(tem_var)
             
            else:
                street_address=(j.p.text)
                city = p[1].text.replace("\xa0","").split( )[0]
                state = p[1].text.replace("\xa0","").split( )[1]
                zipcode ="<MISSING>"

                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append(zipcode)
                store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.thetinfishrestaurants.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[i])
        store.append("thetinfishrestaurants")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(time[i])
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
