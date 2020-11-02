from bs4 import BeautifulSoup
import csv
from sgselenium import SgSelenium
import time
import re #for regular expression

hed=["locator_domain","page_url","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]

driver = SgSelenium().chrome()
time.sleep(2)

url = "https://www.nandos.ca/eat/restaurants"
driver.get(url)
time.sleep(20)
html = driver.execute_script("return document.body.innerHTML")
soup = BeautifulSoup(html,"html.parser")
all_rec = soup.find_all("div",attrs={"class":"state"})
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    for g in all_rec:
        children = g.findChildren()
        state=""
        st = g.findChildren(name="h2")
        for x in st:
               state=x.text
        #children = all_rec.findChildren()
        for child in children:
            locator_domain=""
            location_name=""
            street_address=""
            city=""
            zip_code=""
            country_code=""
            store_number=""
            contact_number=""
            location_type=""
            latitude=""
            langitude=""
            hours_of_operation=""
            stores = child.find_all(name="div",attrs={"class":"city"})
            for x in stores:
                cty = x.find_all(name="div",attrs={"class":"city-info"})
                for y in cty:
                    latitude        =   y["data-lat"]
                    langitude       =   y["data-lng"]
                    contact_number  =   y["data-tel"]
                    if not contact_number:
                    	contact_number = "<MISSING>"
                    hours_of_operation =y["data-ropen"] +","+ y["data-rclose"]
                    
                tt = x.find_all(name="h3",attrs={"class":"title"})
                for y in tt:
                    location_name = y.text
                add = x.find_all(name="p",attrs={"class":"street"})
                for y in add:
                    tem= y.text
                    tem = tem.replace(",,",",") #one record is there which cause problem
                    tem = tem.split(",")
                    zip_code=""
                    street_address = ""
                    for c in range(len(tem)-2):
                        street_address = street_address + tem[c] +" "
                    zip_code = tem[len(tem)-1]
                    if "T8H0W6" in zip_code:
                        zip_code = "T8H 0W6" #one case is there
                    city = tem[len(tem)-2]
                data=["nandos_ca",url,location_name,street_address,city,state,zip_code,"CA","<MISSING>",contact_number,
                      "<MISSING>",latitude,langitude,hours_of_operation]
                fl_writer.writerow(data)
driver.quit()
