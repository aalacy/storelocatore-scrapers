from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('indochino_com')




html = requests.get("https://www.indochino.com/showrooms")
soup = BeautifulSoup(html.text,"html.parser")
 #   location_name=location_name+x.text
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
location_name=street_address=city=state=zip_code=country_code=""
store_number=contact_number=location_type=latitude=longitude=hours_of_operation=""
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    all_rec = soup.find_all("div",attrs={"class":"showroomLocations__LOC cnt-CA js-location"})

    for rec in all_rec:
        latitude = rec["data-latitude"]
        longitude= rec["data-longitude"]
        store_number = rec["data-id"]
        location_name = rec["name"]
        street_address = rec.find("div",attrs={"class":"street"}).text
        street_address = street_address.replace("\n"," ")
        city_st = rec.find("div",attrs={"class":"city"}).text
        city_st = city_st.strip()
        city_st = city_st.split(",")
        city = city_st[0]
        state=city_st[1]
        state = state.strip()
        contact_number = rec.find("div",attrs={"class":"tel"}).text
        contact_number = contact_number.replace(" ","")
        contact_number = contact_number.replace("(","")
        contact_number = contact_number.replace(")","-")
        hrs = rec.find("div",attrs={"class":"showroomLocations__hours"}).text
        hrs = hrs.split("\n")
        hours_of_operation= ""
        for x in hrs:
            if "HOURS" not in x:
                hours_of_operation = hours_of_operation + x +" "
        hours_of_operation = hours_of_operation.strip()
        data=["www_indochino_com",location_name,street_address,city,state,"<MISSING>",
        "CA",store_number,contact_number,"<MISSING>",latitude,longitude,hours_of_operation]
        fl_writer.writerow(data)
        



             #logger.info(data)
            #fl_writer.writerow(data)
