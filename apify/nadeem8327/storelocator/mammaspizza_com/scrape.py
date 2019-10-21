from bs4 import BeautifulSoup
import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy,ProxyType
import time
import re

options = webdriver.ChromeOptions()
prefs= {"profile.default_content_setting_values.geolocation":2}
options.add_argument("--headless")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_experimental_option("prefs",prefs)
driver=webdriver.Chrome('chromedriver',options=options)

url = "https://mammaspizza.com/locations/"
driver.get(url)
html = driver.execute_script("return document.body.innerHTML")

soup = BeautifulSoup(html,"html.parser")
all_rec = soup.find_all(name="div",attrs={"class":"location-item"})
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]

with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    for rec in all_rec:
        street_address=city=state=zip_code=country_code=store_number=contact_number=location_type=phone = hours_of_operation= ""
        store_number = rec["data-id"]
        add = rec.find(name="div",attrs={"class":"loc-info"})
        stre = add.find(name="address")
        location_type = "<MISSING>"
        if "OPENING SOON" in stre.text:
            location_type = "Opening Soon"
        address = stre.text.split("\n")
        if len(address) == 2:
            street_address = address[0]
            city = address[1]
        else:
            name = address[0] +" "+ address[1]
            street_address = name
            city = address[2]
        det = add.find(name="dl")
        det = det.text
        det = det.split("\n")
        i=0
        for x in range(len(det)):
            if i == 2:
                contact_number = det[x]
            elif i>2:
                hours_of_operation = hours_of_operation+ det[x] +" "
            i=i+1
        contact_number = contact_number.replace(" ","-")
        contact_number = contact_number.replace("(","")
        contact_number = contact_number.replace(")","")
        contact_number = contact_number.replace("---","-")
        data=["www_mammaspizza_com",location_type,street_address,city,"<MISSING>","<MISSING>","CA",store_number,contact_number,"<MISSING>","<MISSING>",
         "<MISSING>",hours_of_operation]

        fl_writer.writerow(data)

driver.quit()
