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
    base_url= "https://www.juanmeanburrito.com/locations/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k= (soup.find_all("div",{"class":"loc_list"}))
    v = soup.find("div",{"id":"et-top-navigation"}).find_all("a")[2:][:-5]
    print(v)
    for i in v:
        if i['href'].replace("#",""):
            tem_var=[]
            r = requests.get(i['href'])
            soup1= BeautifulSoup(r.text,"lxml")
            v1 = (list(soup1.find("div",{"class":"et_pb_column et_pb_column_3_8 et_pb_column_inner et_pb_column_inner_1"}).stripped_strings))
            
            tem_var.append("https://www.juanmeanburrito.com")
            tem_var.append(i.text)
            tem_var.append(" ".join(v1[0].split(',')[:-2]))
            tem_var.append(v1[0].split(',')[-2])
            tem_var.append(v1[0].split(',')[-1])
            tem_var.append("<MISSING>")
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(v1[1].replace(" |",""))
            tem_var.append("juanmeanburrito")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(" ".join(v1[5:]))
            return_main_object.append(tem_var)
            # exit()
            # print(i['href'])
   

    # for i in k:
    #     p =i.find_all("div",{"class":'listbox'})
    #     for j in p:
    #         tem_var=[]
    #         name = list(j.stripped_strings)[0]
    #         st = list(j.stripped_strings)[1]
    #         city = list(j.stripped_strings)[2].split(',')[0]
    #         state = list(j.stripped_strings)[2].split(',')[1].split( )[0]
    #         zip1 = list(j.stripped_strings)[2].split(',')[1].split( )[1]
    #         phone = list(j.stripped_strings)[4]
    #         v= list(j.stripped_strings)[5:]

    #         if v[0]=="Fax:":
    #             del v[0]
    #             del v[0]

    #         if v[0] =="Mailing Address:":
    #             del v[0]
    #             del v[0]

    #         if v[0] == "Mailing Address/ Loan Payments:":
    #             del v[0]
    #             del v[0]
    #         if v[0] =="Coin Counter":
    #             del v[0]
    #         hours = " ".join(v)
            
    

    #     tem_var.append("https://www.cfcu.org")
    #     tem_var.append(name)
    #     tem_var.append(st)
    #     tem_var.append(city)
    #     tem_var.append(state)
    #     tem_var.append(zip1)
    #     tem_var.append("US")
    #     tem_var.append("<MISSING>")
    #     tem_var.append(phone)
    #     tem_var.append("cfcu")
    #     tem_var.append("<MISSING>")
    #     tem_var.append("<MISSING>")
    #     tem_var.append(hours)
    #     return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


