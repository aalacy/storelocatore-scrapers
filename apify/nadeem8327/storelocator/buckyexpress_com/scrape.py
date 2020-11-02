from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression


ht = requests.get("http://www.buckysexpress.com/location/chicagoland")
soup = BeautifulSoup(ht.text,"html.parser")
all_rec = soup.find_all('div',attrs={"class":"view-content"})
hed = []
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
#print("length is ",len(hed))
#print(hed)
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    for rec in all_rec:
        od = rec.find_all('div',attrs={"class":"content"})
        for x in od:
            data= x.text
            data = data.replace("\n","")
            sn = x.find("span").text
            store_number= sn.replace(" ","")
            data = data.replace(sn,store_number)
            data = data.replace(store_number,"")
            str_cn = data.split(",")
            str_cn[1] = str_cn[1].replace(" ","")
            street_address = str_cn[0]
            if "IL" in str_cn[1] or "Illi" in str_cn[1]:
                state="Illinois"
            cn_nu = str_cn[1].split("-")
            contact_number = cn_nu[-3][-3:]+"-"+cn_nu[-2]+"-"+cn_nu[-1]
            zip_code=cn_nu[-3][-8:-3]
            street_address = street_address.strip()
            rd=["buckysexpress_com","<MISSING>",street_address,"chicagoland",state,zip_code,"US",store_number,
              contact_number,"<MISSING>","<MISSING>","<MISSING>",24]
            fl_writer.writerow(rd)

        #print(data)
    #print("+++++++++++++++++++++++++++++")
#--------------------------------------- st loius -------------------------- #
    ht = requests.get("http://www.buckysexpress.com/location/greater-st-louis")
    soup = BeautifulSoup(ht.text,"html.parser")
    all_rec = soup.find_all('div',attrs={"class":"view-content"})
    for rec in all_rec:
        od = rec.find_all('div',attrs={"class":"content"})
        for x in od:
            data= x.text
            data = data.replace("\n","")
            sn = x.find("span").text
            store_number= sn.replace(" ","")
            data = data.replace(sn,store_number)
            data = data.replace(store_number,"")
            str_cn = data.split(",")
            street_address = str_cn[0]
            str_cn[1] = str_cn[1].replace(" ","")
            str_cn[1] = str_cn[1].replace("(","")
            str_cn[1] = str_cn[1].replace(")","-")
            str_cn[1] = str_cn[1].strip()
            if "MO" in str_cn[1] or "Illi" in str_cn[1]:
                state="Missouri"
            zip_code = str_cn[1][2:7]
            contact_number = str_cn[1][7:]
            rd=["buckysexpress_com","<MISSING>",street_address,"St. Loius",state,zip_code,"US",store_number,
              contact_number,"<MISSING>","<MISSING>","<MISSING>",24]
            fl_writer.writerow(rd)
#----------------------------houston---------------
    ht = requests.get("http://www.buckysexpress.com/location/houston")
    soup = BeautifulSoup(ht.text,"html.parser")
    all_rec = soup.find_all('div',attrs={"class":"view-content"})
    for rec in all_rec:
        od = rec.find_all('div',attrs={"class":"content"})
        for x in od:
            data= x.text
            data = data.replace("\n","")
            sn = x.find("span").text
            store_number= sn.replace(" ","")
            data = data.replace(sn,store_number)
            data = data.replace(store_number,"")
            str_cn = data.split(",")
            street_address = str_cn[0]
            str_cn[1] = str_cn[1].replace(" ","")
            str_cn[1] = str_cn[1].replace("(","")
            str_cn[1] = str_cn[1].replace(")","-")
            str_cn[1] = str_cn[1].strip()
            if "TX" in str_cn[1] or "Illi" in str_cn[1]:
                state="Texas"
            zip_code = str_cn[1][2:7]
            contact_number = str_cn[1][7:]
            rd=["buckysexpress_com","<MISSING>",street_address,"Houston",state,zip_code,"US",store_number,
              contact_number,"<MISSING>","<MISSING>","<MISSING>",24]
            fl_writer.writerow(rd)
#############-------------------------------------------------###########
    ht = requests.get("http://www.buckysexpress.com/location/omaha-metro")
    soup = BeautifulSoup(ht.text,"html.parser")
    all_rec = soup.find_all('div',attrs={"class":"view-content"})
    for rec in all_rec:
        od = rec.find_all('div',attrs={"class":"content"})
        for x in od:
            data= x.text
            data = data.replace("\n","")
            sn = x.find("span").text
            store_number= sn.replace(" ","")
            data = data.replace(sn,store_number)
            data = data.replace(store_number,"")
            str_cn = data.split(",")
            street_address = str_cn[0]
            str_cn[1] = str_cn[1].replace(" ","")
            str_cn[1] = str_cn[1].replace("(","")
            str_cn[1] = str_cn[1].replace(")","-")
            str_cn[1] = str_cn[1].strip()
            if "NE" in str_cn[1] :
                state="Nebraska"
            elif "IA" in str_cn[1]:
                state="Iowa"
            elif "Ne" in str_cn[1]:
                state="Nebraska"
                str_cn[1] = str_cn[1].replace("Nebraska","NA")

            zip_code = str_cn[1][2:7]
            contact_number = str_cn[1][7:]
            street_address = street_address.strip()
            rd=["buckysexpress_com","<MISSING>",street_address,"<INACCESSIBLE>",state,zip_code,"US",store_number,
              contact_number,"<MISSING>","<MISSING>","<MISSING>",24]
            fl_writer.writerow(rd)
####################################
    ht = requests.get("http://buckysexpress.com/store/buckys-342")
    soup = BeautifulSoup(ht.text,"html.parser")
    all_rec = soup.find_all('div',attrs={"class":"views-row views-row-1 views-row-odd views-row-first views-row-last"})
    for rec in all_rec:
        od = rec.find_all('div',attrs={"class":"content"})
        for x in od:
            data= x.text
            data = data.replace("\n","")
            data = data.split("#")
            store_number = data[0]
            store_number = store_number+"#"+data[1][0:3]
            store_number = store_number.strip()
            str = data[1].split(",")
            street_address = str[0][3:]
            str = str[1].strip()
            str = str.split(" ")
            zip_code=str[1][0:5]
            contact_number = str[1][5:17]

            if "Mi" in str[0] :
                state="Missouri"

            rd=["buckysexpress_com","<MISSING>",street_address,"<INACCESSIBLE>",state,zip_code,"US",store_number,
              contact_number,"<MISSING>","<MISSING>","<MISSING>",24]
            fl_writer.writerow(rd)
        break
