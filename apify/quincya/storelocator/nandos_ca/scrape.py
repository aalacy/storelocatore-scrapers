from bs4 import BeautifulSoup
import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy,ProxyType
import time
import re #for regular expression

hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
opts=Options()
opts.add_argument('disable-infobars')
opts.add_argument("user-agent="+"sara")
opts.add_argument("ignore-certificate-errors")
opts.add_argument("--headless")
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
capabilities = webdriver.DesiredCapabilities.CHROME
driver=webdriver.Chrome('chromedriver',options=opts,desired_capabilities=capabilities)
url = "https://www.nandos.ca/eat/restaurants"
driver.implicitly_wait(60)
driver.get(url)
time.sleep(10)
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
                data=["nandos_ca",location_name,street_address,city,state,zip_code,"CA","<MISSING>",contact_number,
                      "<MISSING>",latitude,langitude,hours_of_operation]
                fl_writer.writerow(data)
driver.quit()
