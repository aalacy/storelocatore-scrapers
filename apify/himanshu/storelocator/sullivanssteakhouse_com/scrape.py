import csv
import requests
# import sqrequests 
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
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
    base_url= "https://sullivanssteakhouse.com/location-search/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k = soup.find_all("div",{"class":"row-location"})
    tag_store = soup.find_all(lambda tag: (tag.name == "script") and "var ld_locations" in tag.text.strip())[-1]
    data = json.loads(tag_store.text.replace("var ld_locations = ",""))
    lat1 =[]
    log1 = []
    state2 = []
    zip1 =[]
    for list1 in data:
        zip1.append(list1['address']['address'].split(",")[-1].split(" ")[-1])
        state2.append(list1['post_title'].split(",")[1])
        lat1.append(list1['address']['lat'])
        log1.append(list1['address']['lng'])
        # print(list1['address']['lat'])
    for index,i in enumerate(k):
        name = i.find("h2").text.split(". ")[-1]
        phone = list(i.find("p").stripped_strings)[-1]
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(list(i.find("p").stripped_strings)[0]))
        state_list = re.findall(r' ([A-Z]{2})', str(str(list(i.find("p").stripped_strings)[0])))
        # print(i.find("p").text.replace("\n",' ').replace("\t",' ').split(","))
        if state_list:
            state = state_list[-1]
        page_url = i.find_all("a")[-1]
        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"
        # else:
        #     zipp = "46240"
        r1 = session.get(page_url['href'])
        soup1= BeautifulSoup(r1.text,"lxml")
        hours = soup1.find("div",{'class':"e9370-13 x-text"}).find("p").text.replace("\n",' ')
        addersss= (str(list(i.find("p").stripped_strings)[0]).replace(zipp,"").replace(state,'').replace(name.split(",")[0],"").replace(",",""))
        tem_var =[]
        tem_var.append("https://sullivanssteakhouse.com/")
        tem_var.append(name)
        tem_var.append(addersss.lstrip())
        tem_var.append(name.split(",")[0])
        tem_var.append(name.split(",")[-1])
        tem_var.append(zip1[index])
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(lat1[index])
        tem_var.append(log1[index])
        tem_var.append(hours)
        tem_var.append(page_url['href'])
        # print(name.split(",")[-1])
        yield tem_var
    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


