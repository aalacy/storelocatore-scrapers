from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression


opts=Options()
opts.add_argument("ignore-certificate-errors")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--headless")
prefs= {"profile.default_content_setting_values.geolocation":2}
opts.add_experimental_option("prefs",prefs)
capabilities = webdriver.DesiredCapabilities.CHROME
driver=webdriver.Chrome("chromedriver",options=opts,desired_capabilities=capabilities)
url= "https://www.jeffersonbank.com/locations"
locator_domain=url
driver.get(url)
html = driver.execute_script("return document.body.innerHTML")

#html = requests.get("https://www.jeffersonbank.com/locations")
#soup = BeautifulSoup(html.text,"html.parser")

soup = BeautifulSoup(html,"html.parser")
 #   location_name=location_name+x.text
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
location_name=street_address=city=state=zip_code=country_code=""
store_number=contact_number=location_type=latitude=longitude=hours_of_operation=""
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    f = soup.find("div",attrs={"class":"view-content"})
    #print(f.text)
    all_rec = f.find_all("div",attrs={"class":"views-row"})
    for x in all_rec:
        location_name= x.find("span",attrs={"class":"field-content"}).text
        street_address = x.find("div",attrs={"class":"thoroughfare"}).text
        city = x.find("span",attrs={"class":"locality"}).text
        state = x.find("span",attrs={"class":"state"}).text
        zip_code = x.find("span",attrs={"class":"postal-code"}).text
        cn = x.find("div",attrs={"class":"views-field views-field-field-phone"})
        contact_number = cn.find("div",attrs={"class":"field-content"}).text
        hours_of_operation = x.find("div",attrs={"class":"views-field views-field-field-lobby-hours"}).text
        hours_of_operation = hours_of_operation + " "+ x.find("div",attrs={"class":"views-field views-field-field-motor-bank-hours"}).text
        contact_number = contact_number.replace(" ","")
        contact_number = contact_number.replace("(","")
        contact_number = contact_number.replace(")","-")
        hours_of_operation = hours_of_operation.strip()
        
        data=["www_jeffersonbank_com",location_name,street_address,city,state,zip_code,
        "US","<MISSING>",contact_number,"<MISSING>","<MISSING>","<MISSING>",hours_of_operation]
        fl_writer.writerow(data)
driver.quit()




             #print(data)
            #fl_writer.writerow(data)
