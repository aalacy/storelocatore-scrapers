from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('alohagas_com')




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
            #handle special case
            if "Mahalo Kilani Mart" in row.text:
                #   logger.info("Yes it is there")
                dta = row.text
                dta = dta.replace("\t","")
                dta = dta.split("\n")
                location_name = dta[0]
                street_address = dta[1].strip()
                contact_number = dta[2].strip()
                contact_number = contact_number.replace(" ","")
                contact_number = contact_number.replace("(","")
                contact_number = contact_number.replace(")","-")
                data=["www_alohagas_com",location_name,street_address,"<MISSING>","<MISSING>","<MISSING>",
                "US","<MISSING>",contact_number,location_type,"<MISSING>","<MISSING>","<MISSING>"]
                fl_writer.writerow(data)

                location_name = dta[4].strip()
                street_address = dta[5].strip()
                contact_number = dta[6].strip()
                contact_number = contact_number.replace(" ","")
                contact_number = contact_number.replace("(","")
                contact_number = contact_number.replace(")","-")
                data=["www_alohagas_com",location_name,street_address,"<MISSING>","<MISSING>","<MISSING>",
                "US","<MISSING>",contact_number,location_type,"<MISSING>","<MISSING>","<MISSING>"]
                fl_writer.writerow(data)


                continue
            dta = row.find("img")
            if "Aloha Airport Cardlock" in row.text:
                shouldPrint = True
            if dta and shouldPrint:
                x = row.text.split("\n")

                #logger.info(row.text)
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


##############HAWAIII######################################
    html2 = requests.get("https://www.alohagas.com/hawaii.html")
    soup2 = BeautifulSoup(html2.text,"html.parser")
     #   location_name=location_name+x.text
    hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
               "longitude","hours_of_operation"]
    location_name=street_address=contact_number=location_type=""

    rows = soup2.find_all("table",attrs={"width":"100%"})
    all_p = rows[0].find_all("tr",attrs={"class":"BodyCopy","valign":"top"})
    i=0
    shouldPrint=False
    place = ""
    city = ""

    for row in all_p:
        span = row.find("span")
        strng = row.find("strong")
        dta = row.find("img")
        if span:
            place = span.text
            place = place.replace("\n","")
            place = place.strip()
        if strng:
            city = strng.text
            city = city.replace("\n","")
            city = city.strip()
        if dta:
            adr = row.text.strip().split("\n")
            for x in range(len(adr)):
                adr[x]=adr[x].strip()
            if "MOUNTAIN" in city and i==0:  #Handle special case
                #logger.info("Special Case")
                place = "Kona"
                location_name = adr[0]
                location_name = location_name.replace(",","'")
                street_address = adr[1]
                street_address = street_address.replace(",","'")
                contact_number= adr[2]
                contact_number = contact_number.replace(" ","")
                contact_number = contact_number.replace("(","")
                contact_number = contact_number.replace(")","-")
                location_type=location_name +" "+place
                data=["www_alohagas_com",location_name,street_address,"<MISSING>","<MISSING>","<MISSING>",
                "US","<MISSING>",contact_number,location_type,"<MISSING>","<MISSING>","<MISSING>"]
                #logger.info(data)
                fl_writer.writerow(data)
                location_name = adr[4]
                location_name = location_name.replace(",","'")
                street_address = adr[5]
                street_address = street_address.replace(",","'")
                contact_number= adr[6]
                contact_number = contact_number.replace(" ","")
                contact_number = contact_number.replace("(","")
                contact_number = contact_number.replace(")","-")
                location_type=location_name +" "+place
                data=["www_alohagas_com",location_name,street_address,"<MISSING>","<MISSING>","<MISSING>",
                "US","<MISSING>",contact_number,location_type,"<MISSING>","<MISSING>","<MISSING>"]
                #logger.info(data)
                fl_writer.writerow(data)

                i=i+1
                #logger.info("---------------------------------------")
            elif "MOUNTAIN" in city and i==1:
                i=i+1
            else:
                if len(adr) == 3:
                   # logger.info("Length is three")
                    location_name = adr[0]
                    location_name = location_name.replace(",","'")
                    street_address = adr[1]
                    street_address = street_address.replace(",","'")
                    contact_number= adr[2]
                    contact_number = contact_number.replace(" ","")
                    contact_number = contact_number.replace("(","")
                    contact_number = contact_number.replace(")","-")
                    location_type=location_name +" "+place
                    data=["www_alohagas_com",location_name,street_address,"<MISSING>","<MISSING>","<MISSING>",
                    "US","<MISSING>",contact_number,location_type,"<MISSING>","<MISSING>","<MISSING>"]
                   # logger.info(data)
                    fl_writer.writerow(data)
                    #logger.info("-------------------------------------------------")
                elif len(adr) == 6:
                    if "(808)" in adr[2]:
                        #logger.info("length is six and 808 is there ")
                        location_name = adr[0]
                        location_name = location_name.replace(",","'")
                        street_address = adr[1]
                        street_address = street_address.replace(",","'")
                        contact_number= adr[2]
                        contact_number = contact_number.replace(" ","")
                        contact_number = contact_number.replace("(","")
                        contact_number = contact_number.replace(")","-")
                        location_type=location_name +" "+place
                        data=["www_alohagas_com",location_name,street_address,"<MISSING>","<MISSING>","<MISSING>",
                        "US","<MISSING>",contact_number,location_type,"<MISSING>","<MISSING>","<MISSING>"]
                        #logger.info(data)
                        fl_writer.writerow(data)
                        location_name = adr[3]
                        location_name = location_name.replace(",","'")
                        street_address = adr[4]
                        street_address = street_address.replace(",","'")
                        contact_number= adr[5]
                        contact_number = contact_number.replace(" ","")
                        contact_number = contact_number.replace("(","")
                        contact_number = contact_number.replace(")","-")
                        location_type=location_name +" "+place
                        data=["www_alohagas_com",location_name,street_address,"<MISSING>","<MISSING>","<MISSING>",
                        "US","<MISSING>",contact_number,location_type,"<MISSING>","<MISSING>","<MISSING>"]
                        fl_writer.writerow(data)
                       # logger.info(data)
                       # logger.info("------------------------------------------------------------------")
                    else:
                       # logger.info("size is six phone not there")
                        location_name = adr[0]
                        location_name = location_name.replace(",","'")
                        street_address = adr[1]
                        street_address = street_address.replace(",","'")
                        contact_number= "<MISSING>"

                        location_type=location_name +" "+place
                        data=["www_alohagas_com",location_name,street_address,"<MISSING>","<MISSING>","<MISSING>",
                        "US","<MISSING>",contact_number,location_type,"<MISSING>","<MISSING>","<MISSING>"]
                        fl_writer.writerow(data)
    html3 = requests.get("https://www.alohagas.com/maui.html")
    soup3 = BeautifulSoup(html3.text,"html.parser")
     #   location_name=location_name+x.text
    hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
               "longitude","hours_of_operation"]
    location_name=street_address=contact_number=location_type=""

    rows = soup3.find_all("table",attrs={"width":"518"})
    all_p = rows[0].find_all("tr",attrs={"valign":"top"})
    i=0
    place = ""
    city = ""

    for row in all_p:
        span = row.find("span")
        strng = row.find("strong")
        dta = row.find("img")
        if span:
            place = span.text
            place = place.replace("\n","")
            place = place.strip()
        if strng:
            city = strng.text
            city = city.replace("\n","")
            city = city.strip()
        if dta:
            #logger.info(place)
            ad= row.text.strip().split("\n")
            location_name = ad[0].strip()
            street_address = ad[1].strip()
            contact_number = ad[2].strip()
            location_type = location_name +" Kahului" #special case
            data=["www_alohagas_com",location_name,street_address,"<MISSING>","<MISSING>","<MISSING>",
            "US","<MISSING>",contact_number,location_type,"<MISSING>","<MISSING>","<MISSING>"]
            fl_writer.writerow(data)
            #logger.info("------------------------------------------")
                      #  logger.info(data)
                      #  logger.info("-----------------------------------------------------")
