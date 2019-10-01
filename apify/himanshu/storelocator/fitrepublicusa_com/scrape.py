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
    base_url= "https://www.fitrepublicusa.com/locations"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    # print(soup)

    k= soup.find("div",{"class":"sqs-block html-block sqs-block-html","id":"block-17db0418b04d7073c0cc"}).find_all("p")
    

    for i in k:
        tem_var=[]
        link =  i.find_all("a")[0]['href'].split("map=")[-1]
        if "https://her.is/2Gi0H5Y" in link:
            lat = "<MISSING>"
            lng = "<MISSING>"
        else:
            lat = i.find_all("a")[0]['href'].split("map=")[-1].split(',')[0]
            lng = i.find_all("a")[0]['href'].split("map=")[-1].split(',')[1]
            print( i.find_all("a")[0]['href'].split("map=")[-1].split(',')[1])
        
        name = list(i.stripped_strings)[0]
        st = list(i.stripped_strings)[1].split("-")[0]
        phone = "-".join(list(i.stripped_strings)[1].split("-")[1:]).strip()
        city = list(i.stripped_strings)[2].split(",")[0]
        state = list(i.stripped_strings)[2].split(",")[1].split( )[0]
        zip1 = list(i.stripped_strings)[2].split(",")[1].split( )[-1].replace("MO","64468")
        print("================")

        tem_var.append("https://www.fitrepublicusa.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append("<MISSING>")
        tem_var.append("https://www.fitrepublicusa.com/locations")
        print(tem_var)
        return_main_object.append(tem_var)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


