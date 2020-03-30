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
    base_url = "https://www.nutritionzoneusa.com"
    r = session.get(base_url)
    main_soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]
    k  = main_soup.find_all("div",{"class":"col sqs-col-6 span-6"})
    for i in k:
        # print(i.find_all('p'))
        for j in i.find_all('h3'):
            if list(j.stripped_strings)  != []:
                if list(j.stripped_strings)[0] == ".":
                    pass
                else:
                    store_name.append(list(j.stripped_strings)[0])
        for index,j in enumerate(i.find_all('p')):
            tem_var=[]
            if list(j.stripped_strings)  != []:
                if list(j.stripped_strings)[0] == ".":
                    pass
                else:
                    state = list(j.stripped_strings)[0].split(',')[-1].split( )[0]
                    # print(list(j.stripped_strings)[0])
                    zip1 = list(j.stripped_strings)[0].split(',')[-1].split( )[1]
                    city = list(j.stripped_strings)[0].split(',')[-2]
                    st = (" ".join(list(j.stripped_strings)[0].split(',')[:2]).replace("Charlotte","").replace("Raleigh","").replace("Santee","").replace("Sylmar","").replace("Lubbock",""))
                    # tem_var.append("https://www.nutritionzoneusa.com")
                    # tem_var.append(store_name[index])
                    tem_var.append(st.strip())
                    tem_var.append(city.strip())
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append("nutritionzoneusa")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    store_detail.append(tem_var)
                    # print(tem_var)
                    # return_main_object.append(tem_var) 


    for i in range(len(store_name)):
       store = list()
       store.append("https://www.nutritionzoneusa.com")
       store.append(store_name[i])
       store.extend(store_detail[i])
       return_main_object.append(store)         
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
