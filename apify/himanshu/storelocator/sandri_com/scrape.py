# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json,urllib
import time
import lxml


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://sandri.com/sandri-convenience-stores/locations/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    tr = soup.find("table",{"style":"border: 1px solid #ccc; width: 100%;","cellspacing":"0","cellpadding":"0","border":"0"}).find_all('tr')
    hours =[]
    return_main_object =[]
    for i in tr:
        data=list(i.stripped_strings)
        for data1 in data:
            time = ''
            alldata = (data1.split(','))
            if len(alldata) ==3:
                pass
            else:
                if 'Store Location' in alldata or 'Hours' in alldata:
                    pass
                else:
                    for data in alldata:
                        time = time +data
                    hours.append(time)



    store_name =[]
    store_detail = []
    k=soup.find_all('script', type='text/javascript')
    for i in k:
        
        if "var maplistScriptParamsKo" in i.text:
            data =  (i.text.replace('/* <![CDATA[ */','').replace('/* ]]> */','').replace("var maplistScriptParamsKo =",'').replace(";",''))
            loaded_json = json.loads(data)
            for i in loaded_json['KOObject']:
                for j in range(0,13):
                    tem_var=[]
                    name =  (str(i['locations'][j]['title']).split(',')[0])
                    store_name.append(name)
                    street_address=i["locations"][j]['address'].replace("<p>",'').replace("</p>",'').replace("<br />",'').replace("\n",',').split(',')[0]
                    city = i["locations"][j]['address'].replace("<p>",'').replace("</p>",'').replace("<br />",'').replace("\n",',').split(',')[1]
                    zipcode1 = i["locations"][j]['address'].replace("<p>",'').replace("</p>",'').replace("<br />",'').replace("\n",',').split(',')[2].split( ) 
                    if len(zipcode1) ==2:
                        zipcode=zipcode1[1]
                    else:
                        zipcode = zipcode1[0]
                    state = (str(i['locations'][j]['title']).split(',')[1])
                    latitude = i['locations'][j]['latitude']
                    longitude = i['locations'][j]['longitude']
                    tem_var.append(street_address)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zipcode)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append(latitude)
                    tem_var.append(longitude)
                    tem_var.append(hours[j])
                    store_detail.append(tem_var)
    for i in range(len(store_name)):
        store = list()
        store.append("https://sandri.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    
    return return_main_object
    



def scrape():
    data = fetch_data()
    write_output(data)

scrape()
