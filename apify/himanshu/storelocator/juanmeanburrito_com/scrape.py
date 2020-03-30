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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://www.juanmeanburrito.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k= (soup.find_all("div",{"class":"loc_list"}))
    v = soup.find("div",{"id":"et-top-navigation"}).find_all("a")[2:][:-5]
    # print(v)
    for i in v:
        if i['href'].replace("#",""):
            tem_var=[]
            r = session.get(i['href'])
            soup1= BeautifulSoup(r.text,"lxml")
            log = (soup1.find("iframe")['src'].split("!2d")[-1].split("!3d")[0])
            lat = (soup1.find("iframe")['src'].split("!2d")[-1].split("!3d")[1].split("!2")[0])
            v1 = (list(soup1.find("div",{"class":"et_pb_column et_pb_column_3_8 et_pb_column_inner et_pb_column_inner_1"}).stripped_strings))
            
            tem_var.append("https://www.juanmeanburrito.com")
            tem_var.append(i.text.replace("NOW OPEN: ",""))
            tem_var.append(" ".join(v1[0].split(',')[:-2]))
            tem_var.append(v1[0].split(',')[-2])
            tem_var.append(v1[0].split(',')[-1])
            tem_var.append("<MISSING>")
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(v1[1].replace(" |",""))
            tem_var.append("<MISSING>")
            tem_var.append(lat)
            tem_var.append(log)
            tem_var.append(" ".join(v1[5:]).encode('ascii', 'ignore').decode('ascii').strip())
            tem_var.append(i['href'])
            return_main_object.append(tem_var)
            # print(tem_var)
           
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


