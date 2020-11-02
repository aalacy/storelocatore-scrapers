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
    base_url= "https://www.mexicanvilla.net/locations-1"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    hours =[]
  
    data=(soup.find_all("div",{"class":"sqs-block-content"}))

    for i in data:
        p = i.find_all("p")
        h = i.find_all("h3")
        h1 = i.find_all("h2")

        for j in h1:
            if j.text.replace("SUBSCRIBE TO MEXICAN VILLA",""):
                store_name.append(j.text.replace("SUBSCRIBE TO MEXICAN VILLA",""))
        for j in h:
            if j.text.split("MEXICAN VILLA")[0]:
                hours.append(j.text.split("MEXICAN VILLA")[0])
        for j in p:
            tem_var =[]
            if len(list(j.stripped_strings))==3:
                tem_var.append(list(j.stripped_strings)[0])
                tem_var.append(list(j.stripped_strings)[1].split(',')[0])
                tem_var.append(list(j.stripped_strings)[1].split(',')[1])
                tem_var.append("<MISSING>")
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(list(j.stripped_strings)[2])
                tem_var.append("mexicanvilla")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.mexicanvilla.net")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(hours[i])
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
