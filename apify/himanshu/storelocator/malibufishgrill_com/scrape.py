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
    base_url= "https://www.malibueatery.com"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k = soup.find(id="locations-1-page").find_all(class_="col sqs-col-6 span-6")
    # links = soup.find_all("div",{"class":re.compile("sqs-block-button-container--left")})
    # for link in links[:3]:
    #     r1 = session.get(link.find("a")['href'])
    #     soup1= BeautifulSoup(r1.text,"lxml")
        # print(soup1.find("div",{"id":"ember1125","class":"ember-view"}))
    for i in k:
        tem_var =[]
        v=(list(i.stripped_strings))
        lat = "<MISSING>"
        lng = "<MISSING>"
        if len(i.a['href'].split("/@"))==2:
            lat = i.a['href'].split("/@")[-1].split(',')[0]
            lng = i.a['href'].split("/@")[-1].split(',')[1]
        elif "EL SEGUNDO" in str(i).upper():
            lat = "33.911745"
            lng= "-118.39452"
        tem_var.append("https://www.malibueatery.com")
        tem_var.append(v[0])
        tem_var.append(v[1])
        tem_var.append(v[2].split(',')[0])
        tem_var.append(v[2].split(',')[1].split( )[0])
        tem_var.append(v[2].split(',')[1].split( )[1])
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(v[3])
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        return_main_object.append(tem_var)
       
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()



