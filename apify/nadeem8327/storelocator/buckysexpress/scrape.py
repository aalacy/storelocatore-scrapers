from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression


ht = requests.get("http://www.buckysexpress.com/location/chicagoland")
soup = BeautifulSoup(ht.text,"html.parser")
all_rec = soup.find_all('div',attrs={"class":"node node-buckys-store view-mode-buckys_location clearfix"})
hed = []
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation","raw_address"]
#print("length is ",len(hed))
#print(hed)
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter='^')
    fl_writer.writerow(hed)
    for rec in all_rec:
        l=str(rec.text).split(",")
        store_number=str(rec.text)[10:13] #store number
        address = l[0][13:]
        if " " in store_number:
            store_number=str(rec.text)[11:14]
            address = l[0][14:]
        postal_code=""
        contact_number = ""
        if "nois" in l[1]:
            postal_code =l[1][7:14]
            contact_number = l[1][14:]
        else:
            postal_code= l[1][3:8]
            contact_number = l[1][8:]
        contact_number=contact_number.replace("\n","")
        rec=[]
        locator_domain= "www_buckysexpress_com"
        rec.append(locator_domain)
        rec.append("<MISSING>")
        rec.append("<INACCESSIBLE>") #street_address
        rec.append("<INACCESSIBLE>") #city
        rec.append("Illinois")
        rec.append("<MISSING>") #zip
        rec.append("US")
        rec.append(store_number)#store_number
        rec.append(contact_number)
        rec.append("<INACCESSABLE>") # location_type
        rec.append("<MISSING>") #latitde
        rec.append("<MISSING>") #longtitude
        rec.append("24") #hour of operation
        rec.append(address + " "+ postal_code) #raw address
        #print(rec)
        fl_writer.writerow(rec)
    #print("+++++++++++++++++++++++++++++")
#--------------------------------------- st loius -------------------------- #

    ht = requests.get("http://www.buckysexpress.com/location/greater-st-louis")
    soup = BeautifulSoup(ht.text,"html.parser")
    all_rec = soup.find_all('div',attrs={"class":"node node-buckys-store view-mode-buckys_location clearfix"})
    for rec in all_rec:
        store_number=str(rec.text)[10:13]  #store_number
        l=str(rec.text).split(",")
        postal_code=l[1][3:7]
        contact_number=l[1][8:]
        contact_number = contact_number.replace(" ","-")
        contact_number = contact_number.replace("(","")
        contact_number = contact_number.replace(")","")
        contact_number = contact_number.replace("\n","")
        raw_address = address +" "+ postal_code
        city = l[0][-9:]
        city = city.replace("\n","")
        address = l[0][14:]
        address = l[0][13:-9]
        state = l[1][:3]
        state = state.replace(" ","")
        data=["www_buckysexpress_com","<MISSING>",address,city,state,"<MISSING>","US",store_number,
              contact_number,"<MISSING>","<MISSING>","<MISSING>",24,raw_address]
        fl_writer.writerow(data)
#--------------------- houston -----------------------------------------------#
    ht = requests.get("http://www.buckysexpress.com/location/houston")
    soup = BeautifulSoup(ht.text,"html.parser")
    all_rec = soup.find_all('div',attrs={"class":"node node-buckys-store view-mode-buckys_location clearfix"})
    for rec in all_rec:
        store_number=str(rec.text)[12:16]  #store_number
        l=str(rec.text).split(",")
        postal_code=l[1][3:8]
        contact_number=l[1][8:]
        contact_number = contact_number.replace(" ","-")
        contact_number = contact_number.replace("(","")
        contact_number = contact_number.replace(")","")
        contact_number = contact_number.replace("\n","")
        city = "houston"
        city = city.replace("\n","")
        address = l[0][14:]
        address = l[0][16:]
        state = l[1][:3]
        state = state.replace(" ","")
        raw_address = address + ","+postal_code
        data=["www_buckysexpress_com","<MISSING>",address,city,state,"<MISSING>","US",store_number,
              contact_number,"<MISSING>","<MISSING>","<MISSING>",24,raw_address]
        fl_writer.writerow(data)

#--------------------------------omaha metro --------------------------------------
    ht = requests.get("http://www.buckysexpress.com/location/omaha-metro")
    soup = BeautifulSoup(ht.text,"html.parser")
    num = soup.find_all('span',attrs={"class":"buckys-color"})
    stn=[]
    for c in num:
        stn.append(c.text)
    i=0
    all_rec = soup.find_all('div',attrs={"class":"node node-buckys-store view-mode-buckys_location clearfix"})
    for rec in all_rec:
        ps = stn[i].split("#")
        store_number = ps[1]
        i=i+1
        l=str(rec.text).split(",")
        address = ""
        fs = l[0].split("#")
        for x in fs[1]:
            if x != "":
                address = address+x
        contact_number=l[1][-14:-1]
        contact_number = contact_number.replace(" ","-")
        contact_number = contact_number.replace("(","")
        contact_number = contact_number.replace(")","")
        contact_number = contact_number.replace("\n","")
        city = "omaha"
        city = city.replace("\n","")
        state = l[1][:3]
        state = "Nebraska"
        raw_address = address+ " "+l[1][:-14]
        data=["www_buckysexpress_com","<MISSING>",address,city,state,"<MISSING>","US",store_number,
              contact_number,"<MISSING>","<MISSING>","<MISSING>",24,raw_address]
        fl_writer.writerow(data)
#-----------------------------------------------Missouri-----------------------------------------#
    ht = requests.get("http://buckysexpress.com/store/buckys-342")
    soup = BeautifulSoup(ht.text,"html.parser")
    # only one record , so i am hardcoding
    data=["www_buckysexpress_com","<MISSING>","4215 S.Highway 169","St Joseph","Missouri","<MISSING>","US",342,
              "816-279-9299","<MISSING>","<MISSING>","<MISSING>",24,"4215 S. Highway 169St Joseph,I-29/Highway 169 interchange"]
    fl_writer.writerow(data)
