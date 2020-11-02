from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression


html = requests.get("http://eatfamouswok.com/locations/")
soup = BeautifulSoup(html.text,"html.parser")
 #   location_name=location_name+x.text
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
location_name=street_address=city=state=zip_code=country_code=""
store_number=contact_number=location_type=latitude=longitude=hours_of_operation=""
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    table = soup.find("table",attrs={"class":"wp-table-reloaded wp-table-reloaded-id-1"})
    all_rec = table.find_all("tr")
    for rec in range(1,len(all_rec)):
         city = all_rec[rec].find("td",attrs={"class":"column-1"}).text
         street_address = all_rec[rec].find("td",attrs={"class":"column-2"}).text
         zip_code= all_rec[rec].find("td",attrs={"class":"column-3"}).text
         state = all_rec[rec].find("td",attrs={"class":"column-4"}).text
         contact_number = all_rec[rec].find("td",attrs={"class":"column-6"}).text
         contact_number = contact_number.replace(" ","")
         contact_number = contact_number.replace("(","")
         contact_number = contact_number.replace(")","-")
         data=["www_eatfamouswok_com","<MISSING>",street_address,city,state,zip_code,
         "US","<MISSING>",contact_number,"<MISSING>","<MISSING>","<MISSING>","<MISSING>"]
         fl_writer.writerow(data)
        
