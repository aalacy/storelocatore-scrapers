from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
import re #for regular expression


opts=Options()
opts.add_argument("ignore-certificate-errors")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--headless")
prefs= {"profile.default_content_setting_values.geolocation":2}
opts.add_experimental_option("prefs",prefs)
capabilities = webdriver.DesiredCapabilities.CHROME
driver=webdriver.Chrome("chromedriver",options=opts,desired_capabilities=capabilities)
url= "https://cremedelacreme.com/locations/"
locator_domain=url
driver.get(url)
html = driver.execute_script("return document.body.innerHTML")
soup = BeautifulSoup(html,"html.parser")
 #   location_name=location_name+x.text
hed=["locator_domain","location_name","street_address","city","state","zip","country_code","store_number","phone","location_type","latitude",
           "longitude","hours_of_operation"]
all_rec = soup.find_all('div',attrs={"class":"wpsl-store-location"})
with open("data.csv",mode="w") as file:
    fl_writer=csv.writer(file,delimiter=',')
    fl_writer.writerow(hed)
    for rec in all_rec:
        name = rec.find("strong").text
        address = rec.find_all("span")
        street_address = address[0].text
        city_zip_state = address[1].text
        hours = rec.find("table",attrs={"class":"wpsl-opening-hours"})
        tm = hours.find_all("tr")
        timing=""
        for x in tm:
            day = x.find_all("td")
            timing = timing + " "+day[0].text+" "

            if day[0].text == "Saturday" or "Sunday":
                timing = timing + " "+day[1].text+" "
            else:
                times = x.find("time")
                timing = timing + " "+times.text+" "
        contact_number = rec.find("a",attrs={"class":"plan-visit-page"})
        store_number = contact_number["class"]
        store_number=store_number[2].split("-")[1]

        contact_number = contact_number.text

        city_zip_state = city_zip_state.strip()
        city_zip_state = city_zip_state.replace(" ","")

        ct=city_zip_state.split(",")
        city=ct[0]
        state = ct[1][:2]
        zip_code = ct[1][2:]
        name=name.replace(",","'")
        street_address = street_address.replace(",","'")
        city=city.replace(",","'")
        zip_code = zip_code.replace(",","'")
        timing = timing.replace(",","'")

        data=["www_cremedelacreme_com",name,street_address,city,state,zip_code,
        "US",store_number,contact_number,"<MISSING>","<MISSING>","<MISSING>",timing]
        fl_writer.writerow(data)


driver.quit()
