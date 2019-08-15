from bs4 import BeautifulSoup
import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy,ProxyType
import time
import re #for regular expression
options = webdriver.ChromeOptions()
prefs= {"profile.default_content_setting_values.geolocation":2}
options.add_experimental_option("prefs",prefs)
driver=webdriver.Chrome('C:\\Users\\Lenovo\\Desktop\\chrome-driver\\chromedriver',options=options)

url = "https://www.dollarstores.com/store-finder/"
driver.get(url)
html = driver.execute_script("return document.body.innerHTML")
#html = requests.get(url)
soup = BeautifulSoup(html,"html.parser")
all_rec = soup.find_all(name="div",attrs={"class":"wpsl-not-loaded"})
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter='^')
    fl_writer.writerow(hed)
    for rec in all_rec:
        street_address=city=state=zip_code=country_code=store_number=contact_number=location_type=phone = hours_of_operation= ""
        store_id = rec.find_all(name="li")
        for store in store_id:
            st_n = store.find(name="div",attrs={"class":"wpsl-store-location"})
            strn = st_n.find(name="strong")
            store_name = strn.text
            store_number = store["data-store-id"]

            stre = store.find_all(name="span")
            street_address = stre[0].text
            city = stre[1].text
            ct = city.split(" ")
            zip_code = ct[-1]+" "+ct[-2]
            state = ct[-3]
            city=""
            for x in range(len(ct)):
                if (ct[x] != state):
                    city= city+ ct[x]+" "
                else:
                    break
            country= stre[2].text
            cn = store.find(name="p",attrs={"class":"wpsl-contact-details"})
            cn = cn.text
            cn = cn.split(" ")
            contact_number = cn[1]
            data=["dollarstores_com",store_name,street_address,city,state,zip_code,"CA",store_number,contact_number.replace("\n",""),"<MISSING>","<MISSING>",
                  "<MISSING>","<MISSING>"]
            print(data)
            fl_writer.writerow(data)
        
driver.quit()
