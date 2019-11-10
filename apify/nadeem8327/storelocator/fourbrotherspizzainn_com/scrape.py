from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression


html = requests.get("http://www.fourbrotherspizzainn.com/locations/")
soup = BeautifulSoup(html.text,"html.parser")
 #   location_name=location_name+x.text
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
location_name=street_address=city=state=zip_code=country_code=""
store_number=contact_number=location_type=latitude=longitude=hours_of_operation=""
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    table = soup.find("section",attrs={"class":"page__content  js-post-gallery  cf"})
    all_rec = table.find_all("div",attrs={"class":"pixcode  pixcode--grid  grid"})
    for rec in all_rec:
         one_rec = rec.find_all("div")
         for one in one_rec:
             location_name = one.find("h5").text
             rc = one.find("p").text
             rc = rc.split("\n")
             street_address = rc[0]
             state_zc = rc[1].split(",")[1]
             state_zc = state_zc.replace(" ","")
             state = state_zc[:2]
             zip_code = state_zc[2:]
             contact_number = rc[2]
             contact_number = contact_number.replace(" ","")
             contact_number = contact_number.replace("(","")
             contact_number = contact_number.replace(")","-")
             city=location_name
             data=["www_fourbrotherspizzainn_com",location_name,street_address,city,state,zip_code,
             "US","<MISSING>",contact_number,"<MISSING>","<MISSING>","<MISSING>","<MISSING>"]
             
             fl_writer.writerow(data)
