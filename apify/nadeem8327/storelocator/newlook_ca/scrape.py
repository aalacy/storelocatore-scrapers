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
options.add_argument("--headless")
driver=webdriver.Chrome('/home/nadeem/Downloads/chromedriver',options=options)

url = "https://www.newlook.ca/en/stores"
driver.get(url)
html = driver.execute_script("return document.body.innerHTML")
#html = requests.get(url)
soup = BeautifulSoup(html,"html.parser")
all_rec = soup.find_all(name="div",attrs={"class":"succuresale-item col-lg-4 col-md-6"})
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    for rec in all_rec:
        street_address=city=state=zip_code=country_code=store_number=contact_number=location_type=phone = hours_of_operation= ""
        store_name = rec.find(name="div",attrs={"class":"succrsale-name"})
        store_name = store_name.text
        
        add = rec.find(name="div",attrs={"class":"succursale-address"})
        add = add.text
        sp = add.split("(")
        street_address = sp[0]
        
        st = sp[1].split(")")
        state = st[0]
        zip_code = st[1]
        
        cty = street_address.split(" ")
        siz = len(cty)
        temp= cty[-2]
        city = ""
        for x in range(len(temp)):
            if not(temp[x].isdigit()):
                city = city + temp[x]
        
        cnt = rec.find(name="div",attrs={"class":"succursale-contact"})
        contact_number = cnt.text
        contact_number = contact_number.replace("T.","")
        
        det = rec.find(name="div", attrs={"class":"succursale-card-actions"})
        hr = det.find(name="a")
        url_det = hr["href"]
        driver2=webdriver.Chrome('chromedriver',options=options)
        driver2.get(url_det)
        html2 = driver2.execute_script("return document.body.innerHTML")
        soup2 = BeautifulSoup(html2,"html.parser")
        det_rec = soup2.find_all(name="li",attrs={"class":"working-hours-item"})
        days = ["Monday","Tuesday","Wedensday","Thursday","Friday","Saturday","Sunday"]
        i = 0
        working_hours = ""
        for x in det_rec:
            hours = x.find(name ="div",attrs={"class":"working-hours"})
            w_hours = hours.text
            if "AM" in w_hours:
                w_hours = w_hours.replace("AM","AM ")
                w_hours = w_hours.replace("PM","PM ")
            y = days[i]+" "+w_hours
            hours_of_operation = hours_of_operation + y
            i = i+1
        driver2.quit()
        store_name = store_name.strip()
        street_address = street_address.strip()
        city = city.strip()
        contact_number = contact_number.strip()
        c = contact_number.split(" ")
        contact_number = c[0]
        zip_code = zip_code.strip()
        state = state.strip()
        data=["www_newlook_ca",store_name.replace("\n",""),street_address.replace("\n",""),city.replace("\n",""),state.replace("\n","")
              ,zip_code.replace("\n",""),"CA","<MISSING>",contact_number.replace("\n",""),"<MISSING>","<MISSING>",
                  "<MISSING>",hours_of_operation.replace("\n","")]
        fl_writer.writerow(data)
        #print(data)
    #print( store_name, ",,,",street_address,",,,",city,",,,",state,",,,,",zip_code,",,,,,CA,,,",contact_number,hours_of_operation)
driver.quit()
