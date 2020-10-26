from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression]

html = requests.get("https://global.tommy.com/int/en/stores")
soup = BeautifulSoup(html.text,"html.parser")
 #   location_name=location_name+x.text
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation","raw_address"]
location_name=street_address=city=state=zip_code=country_code=""
store_number=contact_number=location_type=latitude=longitude=hours_of_operation=""

with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    dls = soup.find_all("div",attrs={"class":"store-info"})
    for dl in dls:
        h1 = dl.find("h1")
        location_name = h1.text
        city_country = dl.find("dd",attrs={"class":"location"})
        city_country = city_country.text
        city = city_country.split(",")[0]
        city=city.strip()
        country = city_country.split(",")[1]
        country=country.strip()
        street_address = dl.find("dd",attrs={"class":"street"})
        street_address = street_address.text
        raw_address = street_address + " "+city
        contact_number = dl.find("dd",attrs={"class":"phone"})
        if contact_number:
            contact_number = contact_number.text
            raw_address = raw_address +" "+contact_number
        else:
            contact_number = "<MISSING>"
        hours_of_operation = dl.find("dd",attrs={"class":"hours"}).text
        hours_of_operation = hours_of_operation.strip()
        if hours_of_operation=="":
            hours_of_operation = "<MISSING>"





        zip_code="<MISSING>"
        latitude="<MISSING>"
        longitude = "<MISSING>"

        contact_number = contact_number.replace("+1","")
        contact_number = contact_number.replace("+","")
        contact_number = contact_number.split("-Adult-Store")[0]
        if "A" in contact_number:
            contact_number = contact_number.strip()
            contact_number = contact_number.split(" ")
            contact_number = contact_number[0]
        if contact_number == "":
            contact_number="<MISSING>"



        data=["www_tommy_com",location_name,street_address,city,"<MISSING>",zip_code,
                "US","<MISSING>",contact_number,"<MISSING>",latitude,longitude,hours_of_operation,raw_address]
                #print(data)
        fl_writer.writerow(data)
#driver.quit()
