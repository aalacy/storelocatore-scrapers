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
    headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"

    }
    base_url= "https://www.happybank.com/Locations"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    address=[]
    k= soup.find('table',{"id":"OfficerList"}).find_all("a")
    for i in k:
        # print(i['href'])
        r = requests.get("https://www.happybank.com/Locations"+i['href'],headers=headers)
        soup1= BeautifulSoup(r.text,"lxml")
        script  = soup1.find_all("script",{"type":"text/javascript"})
        lat= []
        lng=[]
        for i in script:
            if "var jData" in i.text:
                k1 = (i.text.split("var jData =")[1].split("$(function () {")[0].replace(";",""))
                for j in json.loads(k1):
                    tem_var=[]
                    tem_var.append("https://www.happybank.com/")
                    tem_var.append(j['name'])
                    tem_var.append(j['address'])
                    tem_var.append(j["city"])
                    tem_var.append(j["state"])
                    tem_var.append(j['postal'])
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(j['phone'].replace("-BANK",""))
                    tem_var.append("happybank")
                    tem_var.append(j['lat'])
                    tem_var.append(j['lng'])
                    tem_var.append("<MISSING>")
                    if tem_var[3] in address:
                        continue
        
                    address.append(tem_var[3])


                    
                    return_main_object.append(tem_var)
                   
 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


