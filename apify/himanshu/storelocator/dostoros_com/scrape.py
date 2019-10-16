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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://dostoros.com/locations"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k=soup.find_all("div",{'class':"half"})
    hours =[]
    lat1 =[]
    lng1 =[]
    url=[]
    for i in k:
        # print(i.a['href'])
        r = requests.get("https://dostoros.com"+i.a['href'])
        # print("https://dostoros.com"+i.a['href'])
        soup1= BeautifulSoup(r.text,"lxml")
        k1=soup1.find_all("div",{"class":"address"})
        h2=soup1.find_all("div",{"class":"hours"})
        name1=soup1.find_all("div",{"class":"name"})
        for lat in soup1.find_all("div",{'class':'mapit'}):
            if len(lat.a['href'].split('@')) ==2:
                lat1.append(lat.a['href'].split('@')[1].split(',')[0])
                lng1.append(lat.a['href'].split('@')[1].split(',')[1])
            else:
                lat1.append("<MISSING>")
                lng1.append("<MISSING>")

        for j in name1:
            store_name.append(list(j.stripped_strings)[0])
           
        for j in h2:
            hours.append(" ".join(list(j.stripped_strings)))
        for index,j in enumerate(k1):
            tem_var=[]
            st = list(j.stripped_strings)[1]
            city= list(j.stripped_strings)[2].split(",")[0].replace(" NY 10025","")
            zip1 = list(j.stripped_strings)[2].split( )[-1]
            state = list(j.stripped_strings)[2].split( )[-2]
           

            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append("<INACCESSIBLE>")
            tem_var.append("dostoros")
            # tem_var.append(lat1)
            # tem_var.append(lng1)
            # tem_var.append(hours[index])
            url.append("https://dostoros.com"+i.a['href'])
            store_detail.append(tem_var)
            

   
    for i in range(len(store_name)):
        store = list()
        store.append("https://dostoros.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(lat1[i])
        store.append(lng1[i])
        store.append(hours[i].replace("Work or live in the area? Email info@dostoros.com to be added to our pre-opening event list!","<MISSING>"))
        store.append(url[i])
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


