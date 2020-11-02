from bs4 import BeautifulSoup
import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy,ProxyType
import time
import re #for regular expression
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mendes_com')


options = webdriver.ChromeOptions()
prefs= {"profile.default_content_setting_values.geolocation":2}
options.add_experimental_option("prefs",prefs)
options.add_argument("--headless")
driver=webdriver.Chrome('chromedriver',options=options)
url = "https://www.meneds.com/locations/"
driver.get(url)
html = driver.execute_script("return document.body.innerHTML")
soup = BeautifulSoup(html,"html.parser")
#html = requests.get(url)
all_rec = soup.find_all(name="div",attrs={"id":"wpsl-stores"})
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    for rec in all_rec:
        street_address=city=state=zip_code=country_code=store_number=contact_number=location_type=phone = ""
        data=[]
        ul = rec.find(name="ul")
        #logger.info(ul)
        li = ul.find_all("li")
        for l in li:
            store_number = l["data-store-id"]
            stn = l.find("h3")
            for s in stn:
                loc = s
                if "|" in loc:
                    loc = loc.split("|")
                    location_name= loc[1]
                else:
                    location_name = loc
            stree = l.find(name="span",attrs={"class":"wpsl-street"})
            for s in stree:
                street_address=s
            stree = l.find(name="span",attrs={"class":"wpsl-city"})
            for s in stree:
                sp = s.split(",")
                city=sp[0]
                sp = sp[1].split(" ")
                state = sp[1]
                zip_code = sp[2]
            ph = l.find(name="span",attrs={"class":"the-phone"})
            ph = ph.text
            ph = ph.replace("(","")
            ph = ph.replace(")","-")
            ph = ph.replace(" ","")
            phone= ph
            data=["www_meneds_com",location_name,street_address,city,state,zip_code,"US",store_number,phone,"<MISSING>","<MISSING>","<MISSING>","<MISSING>"]
            fl_writer.writerow(data)
driver.quit()
        
