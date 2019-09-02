import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast

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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://www.churchschicken.ca/ontario/locations/"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    
    data = soup.find_all("div",{"class":"hentry","data-sync":"textbox_content"})
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k = soup.find_all("script")

    for i in k:
        if "var map1" in i.text:
            v=(i.text.split('jQuery(document).ready(function($) {var map1 = $("#map1").maps(')[1].split(').data("wpgmp_maps");});')[0])
            v1=(json.loads(v))
            for p in v1['places']:
                tem_var=[]
                zip1 = p['location']['postal_code']
                state= p['location']['state']

                soup1= BeautifulSoup(p['content'],"lxml")
                p2=list(soup1.stripped_strings)

                if p2[0]=='City South Plaza':
                    del p2[0]
                if "Unit 4 and 5," in p2:
                    p2[0]=(" ".join(p2[:2]))
                    del p2[1]

                st = p2[0]
                city = p2[1].split(',')[0]
                zip1=p2[2].split('ON')[-1]
                state = "ON"
                phone = p2[3]

                lat = p['location']['lat']
                lng = p['location']['lng']
                hours = " ".join(p2[4:])
                tem_var.append("https://www.churchschicken.ca")
                tem_var.append(st)
                tem_var.append(st)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zip1)
                tem_var.append("CA")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("churchschicken")
                tem_var.append(lat)
                tem_var.append(lng)
                tem_var.append(hours)
                return_main_object.append(tem_var) 
     
        
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


