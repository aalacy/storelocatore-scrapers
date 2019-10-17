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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation" ,"page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object=[]
    base_url= "https://allsups.com/contact"
    r= requests.get(base_url)
    soup=BeautifulSoup(r.text, "lxml")
    a = soup.find_all("script",{"type":"text/javascript"})
    address=[]
    for i in a:
        
        
        if "new Location" in i.text:
            k =i.text.split('locations.push(new Location(')
            for j in range(len(k)):
                j=(k[j].split('));'))
                tem_var=[]
                
                if len(j[0].split(',')) != 1:
                    city=(j[0].split(',')[1].replace('"',''))
                    
                    store_number=j[0].split(',')[2].replace('"','').split(' ')[2]
                    
                    st=j[0].split(',')[3].replace('"','')
                    
                    if (j[0].split(',')[0].replace('"','')) == "32":
                        state="New Mexico"
                    elif (j[0].split(',')[0].replace('"','')) == "37":
                        state="Oklahoma"
                    else :
                        state="Texas"
                
                    tem_var.append("https://allsups.com")
                    tem_var.append("<MISSING>")
                    tem_var.append(st)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append("<MISSING>")
                    tem_var.append("US")
                    tem_var.append(store_number)
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append("https://allsups.com/contact")
                    print(tem_var)
                    if tem_var[2] in address:
                        continue
                    address.append(tem_var[2])
                    return_main_object.append(tem_var)


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()