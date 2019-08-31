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
    base_url= "https://sunnin.com/santamonica/locations/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k=soup.find_all("div",{"class":"textwidget"})


    base_url1= "https://sunnin.com/westwood/locations/"
    r = requests.get(base_url1)
    soup1= BeautifulSoup(r.text,"lxml")

    k1 = soup1.find_all("div",{"class":"textwidget custom-html-widget"})
   

    for i in k1:
        p = i.find_all("p")
        h = i.find_all('h3')
        for name in h:
            store_name.append(list(name.stripped_strings)[0])

        for j in p:
            tem_var =[]
            street_address = list(j.stripped_strings)[0]
            city = list(j.stripped_strings)[1].split(',')[0]
            state = list(j.stripped_strings)[1].split(',')[1].split( )[0]
            zipcode = list(j.stripped_strings)[1].split(',')[1].split( )[1]
            phone  = list(j.stripped_strings)[-1]
           
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zipcode.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("sunnin")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            store_detail.append(tem_var)

    for index,i in enumerate(k):
        hours = ""
        tem_var =[]
        if list(i.stripped_strings) !=[]:
            if "Mon - Thurs: 11am - 9pm" in  list(i.stripped_strings):
                hours = (" ".join(list(i.stripped_strings)))
            else:
                street_address = list(i.stripped_strings)[0]

                store_name.append(street_address)
                city = list(i.stripped_strings)[1]
                state = list(i.stripped_strings)[2].split( )[0]
                zipcode = list(i.stripped_strings)[2].split( )[1]
                phone  = list(i.stripped_strings)[-1]

             
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zipcode.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("sunnin")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours)
            store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("http://sunnin.com/")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


