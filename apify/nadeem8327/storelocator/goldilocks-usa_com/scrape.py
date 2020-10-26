from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression


html = requests.get("http://www.goldilocks-usa.com/location/")
soup = BeautifulSoup(html.text,"html.parser")
 #   location_name=location_name+x.text
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
location_name=street_address=city=state=zip_code=country_code=""
store_number=contact_number=location_type=latitude=longitude=hours_of_operation=""
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    mr = soup.find("li",attrs={"style":"list-style-type: none;"})
    urls = mr.find_all("li")

    for url in urls:
        #print(url.find("a")["href"])
        new_html = requests.get(url.find("a")["href"])
        soup2 = BeautifulSoup(new_html.text,"html.parser")
        rc = soup2.find("div",attrs={"class":"width_50"})
        location_name = soup2.find("h1",attrs={"class":"entry-title"}).text

        if rc:
            ps = rc.find_all("p")

            for pc in ps:
                rd  =pc.text
                all_rec = rd.split("\n")
                hours_of_operation=""
                for rec in all_rec:
                    #print("00000",rec,"00000")
                    if "Fax:" in rec:
                        contact_number = rec.split("Fax")
                        contact_number = contact_number[0]
                        contact_number = contact_number.replace(" ","")
                        contact_number = contact_number.replace("(","")
                        contact_number = contact_number.replace(")","-")
                    elif "/" in rec:
                        contact_number = rec.split("/")
                        contact_number = contact_number[0]
                        contact_number = contact_number.replace(" ","")
                        contact_number = contact_number.replace("(","")
                        contact_number = contact_number.replace(")","-")
                    if "," in rec and rec.count(",")>=2: # it is an address
                        address = rec.split(",")
                        street_address = address[0]
                        city_zp = address[1]
                        city_zp = city_zp.strip()
                        zip_code = city_zp[:5]
                        city = city_zp[5:]
                        state = address[2]
                    if "PM" in rec and ":" in rec:
                        #print("FOUDN TIME")
                        hours_of_operation =hours_of_operation+rec+" "
            if city == "City": #special scenario
                city = "City Daly"
                state = "CA"
                zip_code = "94014"
            street_address = street_address.replace(",","'")

            city = city.replace(",","'")
            state = state.replace("\n","")
            state = state.strip()
            l = state.split(" ")
            if len(l) == 2 :
                zip_code = state.split(" ")[1]
                state = state.split(" ")[0]
            hours_of_operation = hours_of_operation.replace(",","'")
            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"
            data=["www_goldilocks-usa_com",location_name,street_address,city,state,zip_code,
            "US","<MISSING>",contact_number,"<MISSING>","<MISSING>","<MISSING>",hours_of_operation]
             #print(data)
            fl_writer.writerow(data)
        else:
            ps = soup2.find_all("p")
            hours_of_operation=""
            for c in ps:
                rec=c.text
                if "Fax:" in rec:
                    contact_number = rec.split("Fax")
                    contact_number = contact_number[0]
                    contact_number = contact_number.replace(" ","")
                    contact_number = contact_number.replace("(","")
                    contact_number = contact_number.replace(")","-")
                elif "/" in rec:
                    contact_number = rec.split("/")
                    contact_number = contact_number[0]
                    contact_number = contact_number.replace(" ","")
                    contact_number = contact_number.replace("(","")
                    contact_number = contact_number.replace(")","-")
                if "," in rec and rec.count(",")>=2: # it is an address
                    address = rec.split(",")
                    street_address = address[0]
                    city_zp = address[1]
                    city_zp = city_zp.strip()
                    zip_code = city_zp[:5]
                    city = city_zp[5:]
                    state = address[2]
                if "PM" in rec and ":" in rec:
                    #print("FOUDN TIME")
                    hours_of_operation =hours_of_operation+rec+" "
            street_address = street_address.replace(",","'")
            city = city.replace(",","'")
            hours_of_operation = hours_of_operation.replace(",","'")
            state = state.replace("\n","")
            state = state.strip()
            l = state.split(" ")
            if len(l) == 2 :
                zip_code = state.split(" ")[1]
                state = state.split(" ")[0]
            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"
            data=["www_goldilocks-usa_com",location_name,street_address,city,state,zip_code,
            "US","<MISSING>",contact_number,"<MISSING>","<MISSING>","<MISSING>",hours_of_operation]
             #print(data)
            fl_writer.writerow(data)

            del soup2
