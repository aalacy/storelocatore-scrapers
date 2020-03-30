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
    base_url = "http://nofrillssupermarkets.com/store-location/store-detail"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]
    

    k =  soup.find_all("div",{"class":"location-box"})

    for i in k:
        tem_var =[]
        store_no = list(i.stripped_strings)[0].split("#")[-1]
        name = list(i.stripped_strings)[0].split("#")[0]
        st = list(i.stripped_strings)[1].split(",")[0]
        city = list(i.stripped_strings)[1].split(",")[1]
        state = list(i.stripped_strings)[1].split(",")[2].split( )[0]
        zip1 = list(i.stripped_strings)[1].split(",")[2].split( )[1]
        phone = list(i.stripped_strings)[6]
        time = " ".join(list(i.stripped_strings)[10:20]).replace("Services meat","")
        tem_var.append("http://nofrillssupermarkets.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append(store_no)
        tem_var.append(phone)
        tem_var.append("nofrillssupermarkets")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(time)
        return_main_object.append(tem_var)


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
