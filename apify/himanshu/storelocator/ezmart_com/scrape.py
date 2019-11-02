import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sys

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","raw_address","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url= "https://gpminvestments.com/store-locator/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    # print(soup)
    # exit()
    k= soup.find_all("script",{"type":"text/javascript"})
    
   

    for i in k:
        if "var wpgmaps_localize_marker_data" in i.text:
            response_json = json.loads(i.text.split("var wpgmaps_localize_marker_data =")[1].strip().split("}}};")[0]+"}}}")
            
            for i in (response_json['7'].keys()):
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(response_json['7'][i]['address']))
                tem_var = []
                state_list = re.findall(r' ([A-Z]{2}) ', str(response_json['7'][i]['address'].replace("US","")))
                raw_address  = response_json['7'][i]['address']
                # print( response_json['7'][i]['address'])
                lat = st = response_json['7'][i]['lat']
                lng = st = response_json['7'][i]['lng']
                # if us_zip_list:
                #     # pass
                #     v = response_json['7'][i]['address'].split(",")[0].split("\t")[0].replace(us_zip_list[-1],"").split(".")
                #     if v[-1]=='':
                #         del v[-1]

                #     if len(v) !=2 and len(v) !=1  :
                #         st = (" ".join(v[:-1]).replace("Rt"," Rt 708 / Box 667 ").replace(" U S" , "U S 31" ))
                #     else:
                #         st = " ".join(v)
                # else:
                #     if len(response_json['7'][i]['address'].replace("United States","").replace(", USA","").split(',')) ==1:
                #         st = response_json['7'][i]['address'].replace("United States","").replace(", USA","").split('\t')[0]
                #         city = response_json['7'][i]['address'].replace("United States","").replace(", USA","").split('\t')[1]
                        
                #     else:
                #         v = response_json['7'][i]['address'].replace("United States","").replace(", USA","").split(',')
                #         if v[-1]==' ':
                #             del v[-1]
                        
                #         city = v[1]
                #         st = v[0]

                if us_zip_list:
                    zip1 = us_zip_list[-1]
                else:
                    zip1 = "<MISSING>"

                if state_list:
                    state = state_list[-1]
      
                tem_var.append("https://ezmart.com")
                tem_var.append(response_json['7'][i]['title'])
                tem_var.append("<INACCESSIBLE>")
                tem_var.append("<INACCESSIBLE>")
                tem_var.append(state)
                tem_var.append(zip1)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(lat)
                tem_var.append(lng)
                tem_var.append("<MISSING>")
                tem_var.append(raw_address)
                tem_var.append("https://gpminvestments.com/store-locator/")
                # print(tem_var)
                return_main_object.append(tem_var)
            

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


