from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression


html = requests.get("http://kingtaco.com/locations.html")
soup = BeautifulSoup(html.text,"html.parser")
 #   location_name=location_name+x.text
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
location_name=street_address=city=state=zip_code=country_code=""
store_number=contact_number=location_type=latitude=longitude=hours_of_operation=""
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    all_rec = soup.find_all("article",attrs={"class":"span12"})
    i =0
    for rec in all_rec:
        if i > 0:
            hours_of_operation = ""
            location_name =rec.find("h3").text
            whole_rec = rec.find("strong").text
            whole_rec = whole_rec.replace("\t","")
            whole_rec = whole_rec.split("\n")
            street_address = whole_rec[0]
            ct_zp = whole_rec[1]
            ct_zp = ct_zp.split(",")
            city = ct_zp[0].strip()
            zip = ct_zp[1]
            zip = zip.replace(" ","")
            state = zip[:2]
            zip_code = zip[2:]
            zip_code = zip_code.replace(".","")
            contact_number = whole_rec[2]
            contact_number = contact_number.replace("Phone:","")
            contact_number = contact_number.replace("Phones:","")
            contact_number= contact_number.replace(" ","")
            contact_number = contact_number[:13]
            contact_number = contact_number.replace("(","")
            contact_number = contact_number.replace(")","-")
            if contact_number == "":
                contact_number = "<MISSING>"
            length = len(whole_rec)
            for x in range(3,length):
                hours_of_operation = hours_of_operation +" "+ whole_rec[x]
                hours_of_operation = hours_of_operation.strip()
            store_number = location_name.split("#")
            if len(store_number)>1:
                store_number = store_number[1]
            else:
                store_number = "<MISSING>"

            if hours_of_operation=="":
                hours_of_operation="<MISSING>"
            
            data=["www_kingtaco_com",location_name,street_address,city,state,zip_code,
            "US","<MISSING>",contact_number,"<MISSING>","<MISSING>","<MISSING>",hours_of_operation]
            fl_writer.writerow(data)

        else:
            i=i+1



        #data=["www_indochino_com",location_name,street_address,city,state,"<MISSING>",
        #"CA",store_number,contact_number,"<MISSING>",latitude,longitude,hours_of_operation]
        #fl_writer.writerow(data)




             #print(data)
            #fl_writer.writerow(data)
