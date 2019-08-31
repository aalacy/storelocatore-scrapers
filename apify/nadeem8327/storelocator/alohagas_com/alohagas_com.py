from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression


html = requests.get("https://www.alohagas.com/oahu.html")
soup = BeautifulSoup(html.text,"html.parser")
 #   location_name=location_name+x.text
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
location_name=street_address=contact_number=location_type=""

with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    rows = soup.find_all(attrs={"class":"BodyCopy"})
    i=1
    shouldPrint=False
    place = ""
    for row in rows:
        #dta = row.find("p",attrs={"class":"BodyCopy"})
        strong = row.find("strong")
        if strong:
            place=strong.text.split("\n")[0]
        if row:
            dta = row.find("img")
            if "Aloha Airport Cardlock" in row.text:
                shouldPrint = True
            if dta and shouldPrint:
                x = row.text.split("\n")

                #print(row.text)
                location_name=x[0].strip()
                street_address=x[1].strip()

                if len(x) is 4 and "-" not in x[2]:
                    if "-" in x[3].strip():
                        x[3]=x[3].strip()
                        x[3] = x[3].replace(" ","")
                        x[3] = x[3].replace("(","")
                        x[3] = x[3].replace(")","-")
                        contact_number = x[3]
                else:
                    if "-" in x[2].strip():
                        x[2]=x[2].strip()
                        x[2] = x[2].replace(" ","")
                        x[2] = x[2].replace("(","")
                        x[2] = x[2].replace(")","-")
                        contact_number = x[2]
                location_type = location_name +" "+place
                if "" is contact_number:
                    contact_number = "<MISSING>"
                data=["www_alohagas_com",location_name,street_address,"<MISSING>","<MISSING>","<MISSING>",
                "US","<MISSING>",contact_number,location_type,"<MISSING>","<MISSING>","<MISSING>"]

                fl_writer.writerow(data)


#driver.quit()
