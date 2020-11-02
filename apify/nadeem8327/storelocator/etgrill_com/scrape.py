from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('etgrill_com')




opts=Options()
opts.add_argument("ignore-certificate-errors")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--headless")
prefs= {"profile.default_content_setting_values.geolocation":2}
opts.add_experimental_option("prefs",prefs)
capabilities = webdriver.DesiredCapabilities.CHROME
driver=webdriver.Chrome("chromedriver",options=opts,desired_capabilities=capabilities)
url= "https://www.etgrill.com/contact/brea/"
locator_domain=url
driver.get(url)
html = driver.execute_script("return document.body.innerHTML")
soup = BeautifulSoup(html,"html.parser")
 #   location_name=location_name+x.text
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
lat = soup.find("div",attrs={"class":"gmap"})
tx = lat["data-url"]
tx = tx.split("@")
tx = tx[1]
tx = tx.split(",")
latitude = tx[0]
longitude = tx[1]
#logger.info(latitude,longitude)
all_rec = soup.find('section',attrs={"class":"page__content"})
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    pp = all_rec.find_all('div',attrs={"class":"grid__item"})
    dta = pp[0].find_all("p")
    add = dta[0].text
    street_address = add.split(",")[0]
    city=street_address.strip().split(" ")[3]
    street_address = street_address.strip().split("brea")[0]
    zip_st = add.split(",")[1]
    zip_st = zip_st.strip().replace(" ","")
    state = zip_st[:2]
    zip_code = zip_st[2:]
    tim = pp[1].find("p")
    timing = tim.text
    contact_number = dta[1].text
    contact_number = contact_number.replace(".","-")
    zip_code = zip_code.strip()
    if zip_code == "92621": #this zip code is invalid
        zip_code = "92821"


    data=["www_etgrill_com","<MISSING>",street_address,city,state,zip_code,
    "US","<MISSING>",contact_number,"<MISSING>",latitude,longitude,timing]
    fl_writer.writerow(data)
##################################################
    url= "https://www.etgrill.com/contact/irvine/"
    locator_domain=url
    driver.get(url)
    html = driver.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(html,"html.parser")
    lat = soup.find("div",attrs={"class":"gmap"})
    tx = lat["data-url"]
    tx = tx.split("@")
    tx = tx[1]
    tx = tx.split(",")
    latitude = tx[0]
    longitude = tx[1]
    #logger.info(latitude,longitude)
    all_rec = soup.find('section',attrs={"class":"page__content"})
    pp = all_rec.find_all('div',attrs={"class":"grid__item"})
    dta = pp[0].find_all("p")
    add = dta[0].text
    street_address = add.split(",")[0]
    city=street_address.strip().split(" ")[3]
    street_address = street_address.strip().split("brea")[0]
    zip_st = add.split(",")[1]
    zip_st = zip_st.strip().replace(" ","")
    state = zip_st[:2]
    zip_code = zip_st[2:]
    tim = pp[1].find("p")
    timing = tim.text
    contact_number = dta[1].text
    contact_number = contact_number.replace(".","-")
    zip_code = zip_code.strip()
    if zip_code == "92621": #this zip code is invalid
        zip_code = "92821"
    data=["www_etgrill_com","<MISSING>",street_address,city,state,zip_code,
    "US","<MISSING>",contact_number,"<MISSING>",latitude,longitude,timing]
    fl_writer.writerow(data)
    #logger.info(data)

driver.quit()
