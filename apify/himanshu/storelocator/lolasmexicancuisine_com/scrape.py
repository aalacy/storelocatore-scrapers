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
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url= "https://www.lolasmexicancuisine.com"
    r = session.get(base_url,headers =headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    
    # print(soup)
    # k = (soup.find_all("div",{"class":"tabs-content"}))
    k = (soup.find_all("div",{"class":"wpb_text_column wpb_content_element rollover-details"}))

    for i in k:
        tem_var=[]
        if "View Details" in i.a.text:
            r = session.get(i.a['href'],headers =headers)
            soup1= BeautifulSoup(r.text,"lxml")
            v= soup1.find("div",{"class":"wpb_text_column wpb_content_element address-pannel"})
            name  = list(v.stripped_strings)[0].replace("Address","")
            st = list(v.stripped_strings)[1]
            city = list(v.stripped_strings)[2].split(',')[0]
            state = list(v.stripped_strings)[2].split(',')[1].split( )[0]
            zip1  = list(v.stripped_strings)[2].split(',')[1].split( )[1]
            phone = list(v.stripped_strings)[4:][-1]
            housr = " ".join(list(v.stripped_strings)[4:][:-1])
            # print(" ".join(list(v.stripped_strings)[4:][:-1]))
  
            tem_var.append("https://www.lolasmexicancuisine.com")
            tem_var.append(name)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zip1.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("lolasmexicancuisine")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(housr)
            return_main_object.append(tem_var)
    return return_main_object
   



def scrape():
    data = fetch_data()
    write_output(data)


scrape()


