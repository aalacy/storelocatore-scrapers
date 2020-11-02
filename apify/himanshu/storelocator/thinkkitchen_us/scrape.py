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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
  
    base_url= "http://www.thinkkitchen.us/#social-media"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object=[]
    k = soup.find_all("div",{'class':"textwidget"})

    for i in k:
        tem_var=[]
        if len(list(i.stripped_strings)) !=1:
            name = list(i.stripped_strings)[0]

            stopwords ='NOW OPEN'
            v= list(i.stripped_strings)
            new_words = [word for word in v if word not in stopwords]
            stopwords ='(opening Oct 30/2017)'

            new_words1 = [word for word in new_words if word not in stopwords]
            st = new_words1[2]
            city = new_words1[3].split(',')[0]
            state=(new_words1[3].split(',')[1].replace("H4P 1M7",""))
            zip1 = (new_words1[4].split( )[-1].replace("Canada","H4P 1M7"))
         
            if len(zip1) !=5:
                contry="CA"
            else:
                contry="US"


            tem_var.append("http://www.thinkkitchen.us")
            tem_var.append(name)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state.replace(".",""))
            tem_var.append(zip1)
            tem_var.append(contry)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("http://www.thinkkitchen.us/franchise/")
            if "HEAD OFFICE" in tem_var:
                pass
            else:
                return_main_object.append(tem_var)
   
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




