import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
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
    base_url= "https://www.franklinsynergybank.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    k= soup.find_all("div",{"class":"wpb_column vc_column_container vc_col-sm-12"})
    for i in k:
        names = i.find_all("h2")
        p = i.find_all("div",{"class":"wpb_text_column wpb_content_element"})
        for p1 in p:
           if len(list(p1.stripped_strings)) != 1 and len(list(p1.stripped_strings)) != 0 :
                data = (list(p1.stripped_strings)[0])
                if "Other Information" in data:
                    continue
                try:
                    street_address =list(p1.stripped_strings)[2]
                    city = list(p1.stripped_strings)[3].split(",")[0]
                    state = list(p1.stripped_strings)[3].split(",")[1].split( )[0]
                    zipcode =list(p1.stripped_strings)[3].split(",")[1].split( )[1]
                    phone  = (list(p1.stripped_strings)[4])
                    hours = (list(p1.stripped_strings)[-1])
                    location_type = "Branch"
                except:
                    street_address =list(p1.stripped_strings)[1]
                    city = list(p1.stripped_strings)[2].split(",")[0]
                    state = list(p1.stripped_strings)[2].split(",")[1].split( )[0]
                    zipcode =list(p1.stripped_strings)[2].split(",")[1].split( )[1]
                    phone  = "<MISSING>"
                    hours = "<MISSING>"
                    location_type = "ATM"
                tem_var = []
                tem_var.append("https://www.franklinsynergybank.com")
                tem_var.append(list(p1.stripped_strings)[0])
                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append(zipcode.strip())
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append(location_type)
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hours.replace("Hours: ",""))
                tem_var.append(base_url)
                for i in range(len(tem_var)):
                    if type(tem_var[i]) == str:
                        tem_var[i] = ''.join((c for c in unicodedata.normalize('NFD', tem_var[i]) if unicodedata.category(c) != 'Mn'))
                tem_var = [x.replace("–","-") if type(x) == str else x for x in tem_var]
                tem_var = [x.strip() if type(x) == str else x for x in tem_var]
                yield tem_var
def scrape():
    data = fetch_data()
    write_output(data)
scrape()


