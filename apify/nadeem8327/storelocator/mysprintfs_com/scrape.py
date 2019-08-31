from bs4 import BeautifulSoup
import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy,ProxyType
import time
import re #for regular expression

hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
opts=Options()
opts.add_argument('disable-infobars')
opts.add_argument("user-agent="+"sara")
opts.add_argument("ignore-certificate-errors")
#capabilities = webdriver.DesiredCapabilities.CHROME
#driver=webdriver.Chrome('C:\\Users\\Lenovo\\Desktop\\chrome-driver\\chromedriver',options=opts,desired_capabilities=capabilities)
url = "https://mysprintfs.com/locations"


time.sleep(3)
html = requests.get(url)
soup = BeautifulSoup(html.text,"html.parser")
all_rec = soup.find_all("div",attrs={"class":"all-results"})
main_url = "https://mysprintfs.com"
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    for g in all_rec:
        st = g.find_all(name="div",attrs={"class":"results"})
        for record in st:
            locator_domain="www_mysprintfs_com"
            location_name=""
            street_address=""
            city=""
            zip_code=""
            country_code=""
            store_number=""
            contact_number=""
            location_type=""
            latitude=""
            langitude=""
            hours_of_operation=""
            state=""
            loc = record.find("a")
            urll=""
            for x in loc:
                store_number = x[:10]
                ct = x.split(",")
                if ct == []:
                    city="<MISSING>"
                else:
                    city=ct[0][10:]
                if ct == "" or len(ct)==1:
                    city="<MISSING>"
                    
                if x[-2:] == "SC":
                    state="South Carolina"
                elif x[-2:] == "GA":
                    state="Georgia"
                else:
                    state="<MISSING>"
                urll = loc["href"]
            urll = main_url + urll
            adrs = record.find(name="p",attrs={"class":"addr"})
            for ad in adrs:
                street_address = ad
                zip_code = ad[-6:]
            #data for record Store #Store #722 Louisville, GA202/204 Hwy 1 N Bypass, 30834
            #was wrong , so i am adding one condioitn here
            if "202/204 Hwy" in street_address:
                state= "Colorado"
            street_address = street_address.replace(",","'")
            city = city.replace(",","'")
            state = state.replace(",","'")
            extended_html = requests.get(urll)
            dt = BeautifulSoup(extended_html.text,"html.parser")
            location = dt.find_all(name="div", attrs={"class":"location-button"})
            for lloc in location:
                cnt = lloc.find("a")
                contact_number = cnt.text
            contact_number = contact_number.replace(".","-")
            data=[locator_domain,"<MISSING>",street_address,city,state,zip_code,"US",store_number,contact_number,"<MISSING>",
                  "<MISSING>","<MISSING>","<MISSING>"]
            fl_writer.writerow(data)
            
