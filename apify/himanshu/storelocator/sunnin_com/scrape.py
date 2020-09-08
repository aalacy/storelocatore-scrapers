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
    base_url= "http://sunnin.com/location.html"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k=soup.find_all("div",{"class":"col-md-6"})

    for i in k:
        tem_var=[]
        latitude=''
        longitude =''
        if "Contact Us" in i.text:
            r = session.get("http://sunnin.com/"+i.a['href'])
            page_url = "http://sunnin.com/"+i.a['href']
            soup1= BeautifulSoup(r.text,"lxml")
            v= soup1.find_all("div",{"class":"description"})[-1]
            # print(soup1.find("div",{'class':"col-lg-12 maps animated"}).iframe['src'].split("2d")[1].split("!2m")[0].split("!3d")[0])
            latitude=soup1.find("div",{'class':"col-lg-12 maps animated"}).iframe['src'].split("2d")[1].split("!2m")[0].split("!3d")[1]
            longitude= soup1.find("div",{'class':"col-lg-12 maps animated"}).iframe['src'].split("2d")[1].split("!2m")[0].split("!3d")[0]

            hours = (" ".join(list(v.stripped_strings)))
        if list(i.stripped_strings) != []:
            st=list(i.stripped_strings)[1]
            store_name.append(list(i.stripped_strings)[0])
            city = list(i.stripped_strings)[2].split(',')[0]
            state = list(i.stripped_strings)[2].split(',')[1].split( )[0]
            zip1 = list(i.stripped_strings)[2].split(',')[1].split( )[1]
            phone = list(i.stripped_strings)[3]

        else:
            pass

        tem_var.append(st.replace(".,",""))
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zip1.strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append(hours)
        tem_var.append(page_url)
        # print(str(tem_var))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("http://sunnin.com/")
        store.append(store_name[i])
        store.extend(store_detail[i])
        # print(str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


