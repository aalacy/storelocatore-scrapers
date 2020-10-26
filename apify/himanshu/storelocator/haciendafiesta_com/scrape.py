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
    base_url= "https://haciendafiesta.com/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    # print(soup.find_all('div',{"class":"location"}))
    k= soup.find_all('div',{"class":"location"})
    for i in k:
        tem_var=[]
        # print(i.h3.a['href'])
        r = session.get("https://haciendafiesta.com"+i.h3.a['href'])
        soup1 = BeautifulSoup(r.text,"lxml")
        name = list(soup1.find("div",{"class":"location-summary"}).stripped_strings)[0]
        st = list(soup1.find("div",{"class":"location-summary"}).stripped_strings)[2]
        v = list(soup1.find("div",{"class":"location-summary"}).stripped_strings)
        # print(list(soup1.find("div",{"class":"location-summary"}).stripped_strings))
        # exit()
        # time = (" ".join(list(soup1.find("div",{"class":"location-description"}).stripped_strings)).replace("\xa0",""))
        h1 = soup1.find("table")
        if h1 != None:
            time = (" ".join(list(h1.stripped_strings)).replace("Hours: ",""))
        else:
            time = (" ".join(list(soup1.find("div",{"class":"location-description"}).stripped_strings)).replace("\xa0",""))
        # print(time)
        tem_var.append("https://haciendafiesta.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(v[3].split(',')[0])
        tem_var.append(v[3].split(',')[1].split( )[0])
        tem_var.append(v[3].split(',')[1].split( )[1])
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(v[4])
        tem_var.append("haciendafiesta")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(time.replace("\u202a","").replace("\u202c",""))
        return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


