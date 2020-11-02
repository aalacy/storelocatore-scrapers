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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://www.gamestop.it/StoreLocator/GetStoresForStoreLocatorByProduct?value=&skuType=0&language=it-IT"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    
    k =json.loads(soup.text)
    
    for i in k:
        tem_var=[]

        if "undefined" in  i["Address"]:
            pass
        else:

            if "undefined" in i['StreetNumber']:
                st = i['Address']
            else:
                st =i['StreetNumber']+ ' ' + i['Address']

            
            city = i['City'].replace("undefined","<MISSING>")

            state = i['Province'].replace("undefined","<MISSING>")

            if "undefined" in i['Hours']:
                hours = "<MISSING>"
            else:
                soup1= BeautifulSoup(i['Hours'],"lxml")
                hours = (" ".join(list(soup1.stripped_strings)).replace("hiuso i giorni festivi. Gli orari indicati non comprendono variazioni straordinarie di orario o di apertura. Per maggiori informazioni contatta direttamente il negozio al numero che trovi qua sotto.","").replace("Domenica Chiusura Settimanale C","").replace("Domenica Chiuso C","").replace("C",""))

            lat = i["Latitude"].replace("undefined","<MISSING>")
            log = i["Longitude"].replace("undefined","<MISSING>")
            name = i['Name']
            phone = i["Phones"].replace("undefined","<MISSING>")
            zip1 = i['Zip'].replace("undefined","<MISSING>")

            
            tem_var.append("https://www.gamestop.it")
            tem_var.append(name)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone.replace("039/9000417 - ","").replace("071-9280820/",""))
            tem_var.append("gamestop")
            tem_var.append(lat)
            tem_var.append(log)
            tem_var.append(hours.replace("Il presente non � un negozio aperto al pubblico e alla vendita.","<MISSING>"))
            return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


