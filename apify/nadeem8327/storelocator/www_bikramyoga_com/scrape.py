from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression

country_codes={
    'Chile':"CL",'Poland':"PL", 'Switzerland':"CH", 'Mexico':"MX", 'India':"IN", 'Australia':"AU", 'Austria':"AT", 'Philippines':"PH", 'USA':"US",
    'United States':"US", 'Canada':"CA", 'Jamaica':"JM",'Czech Republic':"CZ", 'France':"FR", 'Peru':"PE", 'Germany':"DE",
    'Scotland':"GB", 'Norway':"NO", 'Belgium':"BL", 'Hanover, Massachusetts':"<MISSING>", 'Argentina':"AR",
    'KENYA':"KE",'Italy':"IT",'Japan':"JP",'Spain':"ES",
    }


opts=Options()
opts.add_argument("ignore-certificate-errors")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--headless")
capabilities = webdriver.DesiredCapabilities.CHROME
driver=webdriver.Chrome("chromedriver",options=opts,desired_capabilities=capabilities)
url= "https://www.bikramyoga.com/studios/studio-locator/"
locator_domain=url
driver.get(url)
html = driver.execute_script("return document.body.innerHTML")
soup = BeautifulSoup(html,"html.parser")
 #   location_name=location_name+x.text
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation","raw_address"]
all_rec = soup.find_all('div',attrs={"class":"results_wrapper"})
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    for rec in all_rec:
        name = rec.find("span",attrs={"class":"location_name"}).text
        street_address = rec.find("span",attrs={"class":"slp_result_address slp_result_street"}).text
        city_zip = rec.find("span",attrs={"class":"slp_result_address slp_result_citystatezip"}).text
        state = rec.find("span",attrs={"class":"slp_result_address slp_result_country"}).text
        contact_number = rec.find("span",attrs={"class":"slp_result_address slp_result_phone"}).text
        raw_address = street_address + city_zip
        name = name.replace(",","'")
        street_address = street_address.replace(",","'")
        if street_address == "":
            street_address="<MISSING>"
        state = state.replace(",","'")
        if state=="":
            state="<INACCESSIBLE>"
        contact_number = contact_number.replace(","," ")
        if contact_number == "":
            contact_number="<MISSING>"
        raw_address = raw_address.replace(",","'")
        data=["www_bikramyoga_com",name,street_address,"<INACCESSIBLE>",state,"<INACCESSIBLE>",
        "<INACCESSIBLE>","<MISSING>",contact_number,"<MISSING>","<MISSING>","<MISSING>","<MISSING>",raw_address]
        fl_writer.writerow(data)


driver.quit()
