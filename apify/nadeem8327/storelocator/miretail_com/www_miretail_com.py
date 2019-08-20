from bs4 import BeautifulSoup
import requests
import csv
import re #for regular expression

code_dic ={" South Africa":"ZA"," China":"CN"," Bulgaria":"BG"," France":"FR",
           " Ireland":"IE"," UK":"UK"," Canada":"CA"," USA":"USA"," Australia":"AU"}
th = requests.get("https://mi9retail.com/contact-us/")
sp = BeautifulSoup(th.text,"html.parser")
all_rec = sp.find_all("div",attrs={"class":"fusion-text"})
i=1
city=""
country=""
state=""
address=""
contact_number=""
zip_code=""
country_code=""
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    for rec in all_rec:
        if(i>4):
            zip_code=""
            address =""
            dt = rec.text.split("\n")
            city=dt[0].split(",")[0]
            country= dt[0].split(",")[1]
            #country=
            country_code=code_dic[country]
            adr= dt[1].split("|")
            if len(adr)>0:
                address = adr[0]           
            else:
                ad=dt[1].split(",")
                for x in range(len(ad)-1):
                    address = address+" "+x
            zp = dt[1].split(" ")
            zip_code = zp[len(zp)-1]
            if not zip_code.isdigit():
                zip_code="<MISSING>"
            if "Tel" in dt[2]:
                contact_number=dt[2][4:]
            else:
                address = address +" "+ dt[2]
            contact_number=contact_number.replace(".","-")
            data=["www_mi9retail_com","<MISSING>",address,city,"<MISSING>",zip_code,country_code,"<MISSING>",contact_number,"<MISSING>",
                  "<MISSING>","<MISSING>","<MISSING>"]
            fl_writer.writerow(data)
        elif i==4 :
            d= rec.text.split("\n")
            address = d[0]
            country= d[1].split("|")[1]
            country_code = code_dic[country]
            city= d[1].split(",")[0]
            zip_code = d[1][11:16]
            data=["www_mi9retail_com","<MISSING>",address,city,"<MISSING>",zip_code,country_code,"<MISSING>","<MISSING>","<MISSING>",
                  "<MISSING>","<MISSING>","<MISSING>"]
            fl_writer.writerow(data)
        i=i+1
