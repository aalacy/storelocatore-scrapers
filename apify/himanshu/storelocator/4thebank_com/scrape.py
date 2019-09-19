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
    base_url= "https://www.4thebank.com/locations/?atm=&branch=&loc=&state="
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    marker  = soup.find_all("marker")
    for i in marker:
        tem_var =[]
        if i['lobbyhours']:
            time = i['lobbyhours'].replace("<br/>",'').replace("\n"," ").replace("<br>"," ")+ ' ' +" ".join(i['driveuphours'].split("<br/>")).replace("\n","").replace("<br/>","")
        else:
            time = "<MISSING>"
        tem_var.append("https://www.4thebank.com")
        tem_var.append(i['name'])
        tem_var.append(i['address'])
        tem_var.append(i['city'])
        tem_var.append(i['state'])
        tem_var.append(i['zipcode'])
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(i['phone'] if i['phone'] else "<MISSING>")
        tem_var.append("4thebank")
        tem_var.append(i['lat'])
        tem_var.append(i['lng'])
        tem_var.append(time if time else "<MISSING>")
        return_main_object.append(tem_var)
       

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


