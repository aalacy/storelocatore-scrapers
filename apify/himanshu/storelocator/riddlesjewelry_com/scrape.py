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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    base_url= "https://www.riddlesjewelry.com/storelocator/index/loadstore/"
    r = session.get(base_url,headers = headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k = (json.loads(soup.text))
    # print(k)
    for idx, val in enumerate(k['storesjson']):
        tem_var=[]
        street_address =''
        street_address1 = val["address"].split(',')
        phone = val["phone"]
        latitude = val["latitude"]
        longitude =val["longitude"]
        zipcode = val['zipcode']
        state =val['state']
        city = val['city']
        # print(city)
        store_name.append(val['store_name'])
        if len(street_address1)==2:
            street_address= (street_address1[0])
        else:
            street_address =(street_address1)[0]
        tem_var.append(street_address)
        tem_var.append(city if city else "<MISSING>" )
        tem_var.append(state if state else "<MISSING>" )
        tem_var.append(zipcode if zipcode else "<MISSING>")
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("riddlesjewelry")
        tem_var.append(latitude)
        tem_var.append(longitude)
        data8 = str(city.replace(" ","_"))+"-"+str(state.replace(" ","_"))+"-"+str(zipcode)
        data =("https://www.riddlesjewelry.com/riddles-jewelry-store"+"-"+str(data8)).replace('Dickinson-North_Dakota-58601',"Dickinson-North-Dakota-58601").replace("North_Dakota-58401",'NorthDakota-58401').replace("s-jewelry-store-Bloomington-Minnesota-55425",'-s-jewelry-mall-of-america').replace("s-jewelry-store-Dubuque-Iowa-52002","-s-jewelry-dubuque-iowa").replace("riddles-jewelry-store-Pueblo-Colorado-81008","pueblo-co-riddles-jewelry")
        if "2200 N Maple Ave" in street_address:
            data = data.replace("Dakota-57701","dakota-57701-44")
        if "2707 Mt Rushmore Rd" in street_address:
            data = data.replace("Dakota-57701","dakota-57701-45-45")
        if "202 Disk Drive" in street_address:
            data = data.replace("Dakota-57701","dakota-57701-45")
        page_url = data
        r1 = session.get(page_url,headers = headers)
        soup1= BeautifulSoup(r1.text,"lxml")
        try:
            hours_of_operation = " ".join(list(soup1.find("table",{"class":"table table-hover table-striped"}).stripped_strings))
        except:
            hours_of_operation = ("<MISSING>")
        tem_var.append(hours_of_operation)
        tem_var.append(page_url)
        store_detail.append(tem_var)
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.riddlesjewelry.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
