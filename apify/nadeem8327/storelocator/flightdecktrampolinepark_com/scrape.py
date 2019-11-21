from bs4 import BeautifulSoup
import requests
import csv
import re #for regular expression

th = requests.get("http://www.flightdecktrampolinepark.com/")
sp = BeautifulSoup(th.text,"html.parser")
time = sp.find_all("p",attrs={"class":"font_0"})
tm = ""
for x in time:
    if ":" in x.text:
        tm = tm+x.text+","
ht = requests.get("http://www.flightdecktrampolinepark.com/contact")
soup = BeautifulSoup(ht.text,"html.parser")
all_rec = soup.find_all('p',attrs={"class":"font_0"})
hed = []
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
record = []
phone=""
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    for rec in all_rec:
        if "-" in rec.text:
            ph = rec.text.split(" ")
            ph[0]=ph[0].replace("(","")
            ph[0]=ph[0].replace(")","")
            phone = ph[0]+"-"+ph[1]
    for rec in all_rec:
        if "," in rec.text :
            add = rec.text.split(",")
            address=add[0]
            city = add[1]
            st = add[2].split(" ")
            state = st[1]
            postal_code= st[2]
            data=["www_flightdecktrampolinepark_com","<MISSING>",address,city,state,"<MISSING>","US","<MISSING>",
                  phone,"<MISSING>","<MISSING>","<MISSING>",tm]
            fl_writer.writerow(data)
        
