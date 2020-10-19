import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url= "https://www.crabbyjoes.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    hours = []
    name_store=[]
    store_detail=[]
    phone=[]
    return_main_object=[]
    k=(soup.find_all("div",{"id":"locations","class":"locations2"}))
    for i in k:
        p =i.find_all("li",{"class":"equal"})
        for j in p:
            if "9155.29 KM" in list(j.stripped_strings)[1] :
                continue
            latitude = (j.attrs['onclick'].split('(')[1].split(");")[0].split(',')[0])
            longitude  = (j.attrs['onclick'].split('(')[1].split(");")[0].split(',')[1])
            tem_var=[]
            name = list(j.stripped_strings)[0]
            st = list(j.stripped_strings)[2]
            city = list(j.stripped_strings)[3].split(',')[0]
            state = list(j.stripped_strings)[3].split(',')[1].split( )[0]
            zipcode =" ".join(list(j.stripped_strings)[3].split(',')[1].split( )[1:])
            phone =list(j.stripped_strings)[7]
            hours = " ".join(list(j.stripped_strings)[10:][:-1])
            if len(zipcode)!=5:
                coutry = "CA"
            else:
                coutry = "US"
            tem_var.append("https://www.crabbyjoes.com")
            tem_var.append(name)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append(coutry)
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("crabbyjoes")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hours if hours else "<MISSING>")
            tem_var.append("https://www.crabbyjoes.com/locations/")
            yield tem_var
def scrape():
    data = fetch_data()
    write_output(data)
scrape()





