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
    base_url= "https://www.signaturestyle.com/salon-directory.html"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    for d in soup.find_all("div",{"class":"acs-commons-resp-colctrl-row section"}):
        for k in d.find_all("a",{"class":"btn btn-primary"}):
            # base_url= 
            r1 = requests.get("https://www.signaturestyle.com"+k['href'])
            soup1= BeautifulSoup(r1.text,"lxml")
            for herf in soup1.find_all("div",{"class":"salon-group col-md-10 col-xs-12"}):
                for href1 in herf.find_all("a"):
                    r2 = requests.get("https://info3.regiscorp.com/salonservices/siteid/100/salon/"+href1['href'].split("-")[-1].replace(".html",'')).json()
                    tem_var =[]
                    for h in r2['store_hours']:
                        hours = (h['days']+ ' '+ h['hours']['open'] + ' '+h['hours']['close'])
                    tem_var.append("https://www.signaturestyle.com/brands/first-choice-haircutters.html")
                    tem_var.append(r2['name'])
                    tem_var.append(r2['address'])
                    tem_var.append(r2['city'])
                    tem_var.append(r2['state'])
                    tem_var.append(r2['zip'])
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(r2['phonenumber'])
                    tem_var.append("<MISSING>")
                    tem_var.append(r2['longitude'])
                    tem_var.append(r2['latitude'])
                    tem_var.append(hours)
                    tem_var.append("https://www.signaturestyle.com/"+href1['href'])
                    #print("~~~~~~~~~~~~~~`",tem_var)
                    yield tem_var
                 

    #         tem_var.append("https://www.cfcu.org")
    #         tem_var.append(name)
    #         tem_var.append(st)
    #         tem_var.append(city)
    #         tem_var.append(state)
    #         tem_var.append(zip1)
    #         tem_var.append("US")
    #         tem_var.append("<MISSING>")
    #         tem_var.append(phone)
    #         tem_var.append("cfcu")
    #         tem_var.append("<MISSING>")
    #         tem_var.append("<MISSING>")
    #         tem_var.append(hours)
    #         print(tem_var)
    #         return_main_object.append(tem_var)
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


