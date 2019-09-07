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
    base_url= "https://bluesushisakegrill.com/locations/ohio/westlake/crocker-park"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone1 =[]
    data = soup.find("div",{"class":"location_details-address"})

    data1 = soup.find("div",{"class":"single_location-information-top"})
    latitude  = (data1.a['href'].split("&ll=")[-1].split("+-")[0])
    longitude  =  data1.a['href'].split("&ll=")[-1].split("+-")[1]
    phone  =(list(data1.stripped_strings)[4])
    hours = (" ".join(list(data1.stripped_strings)[8:]))
    street_address = (data.p.text.replace("flagship_locationselect_color","").replace("\n","").split('W')[0])
    city = data.p.text.replace("flagship_locationselect_color","").replace("\n","").split('d')[1].split(",")[0]
    state =  data.p.text.replace("flagship_locationselect_color","").replace("\n","").split('d')[1].split(",")[1].split( )[0]
    zipcode =  data.p.text.replace("flagship_locationselect_color","").replace("\n","").split('d')[1].split(",")[1].split( )[1]
   
    tem_var =[]

    tem_var.append(street_address)
    store_name.append(street_address)
    tem_var.append(city)
    tem_var.append(state)
    tem_var.append(zipcode)
    tem_var.append("US")
    tem_var.append("<MISSING>")
    tem_var.append(phone)
    tem_var.append("bluesushisakegrill")
    tem_var.append(latitude)
    tem_var.append(longitude)
    tem_var.append(hours)
    store_detail.append(tem_var)


    for i in range(len(store_name)):
        store = list()
        store.append("https://bluesushisakegrill.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

