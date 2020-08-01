import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import urllib3
from selenium.webdriver.support.wait import WebDriverWait
from sgselenium import SgSelenium

urllib3.disable_warnings()



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    driver = SgSelenium().firefox()
    driver1 = get_driver()
    driver.get("https://kwiktrip.com/Maps-Downloads/Store-List")
    locator_domain = "https://kwiktrip.com"
    hours_of_operation ="<MISSING>"
    # print(soup.find_all("table",{"id":"tablepress-4"}))
    while True:
        soup = BeautifulSoup(driver.page_source,"lxml")
        for data in soup.find_all("tbody",{"class":"row-hover"}):
            for tr in data.find_all("tr"):
                store_number = list(tr.stripped_strings)[0]
                # print("https://www.kwiktrip.com/locator/store?id="+str(store_number))
                driver1.get("https://www.kwiktrip.com/locator/store?id="+str(store_number))
                soup1 = BeautifulSoup(driver1.page_source,"lxml")

                try:
                    h = soup1.find("div",{"class":"Store__dailyHours"})
                    if h != None:
                        hours_of_operation =  " ".join(list(h.stripped_strings))
                except:
                    h = soup1.find("div",{"class":"Store__open24Hours"})
                    hours_of_operation = " ".join(list(h.stripped_strings))
                # print(" ".join(list(soup1.find("div",{"class":"Store__open24Hours"}).stripped_strings)))
                page_url = "https://www.kwiktrip.com/locator/store?id="+str(store_number)
                location_name = list(tr.stripped_strings)[1]
                street_address = list(tr.stripped_strings)[2]
                city = list(tr.stripped_strings)[3]
                state = list(tr.stripped_strings)[4]
                zipp = list(tr.stripped_strings)[5]
                phone = list(tr.stripped_strings)[6]
                latitude = list(tr.stripped_strings)[7]
                longitude = list(tr.stripped_strings)[8]
                # page_url ="<MISSING>"
                location_type = "<MISSING>"
                country_code = "US"
                store =[]
                if hours_of_operation.strip():
                    hours_of_operation1= hours_of_operation
                else:
                    hours_of_operation1 = "<MISSING>"

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation1, page_url]

                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                # print("~~~~~~~~~~~~~~~~~~~~~~  ",store)
                yield store
                # print(list(tr.stripped_strings))

        soup1 = BeautifulSoup(driver.page_source,"lxml")
        if soup1.find("a",{"id":"tablepress-4_next"}):
            driver.find_element_by_xpath("//a[@id='tablepress-4_next']").click()
        else:
            break
        if soup1.find("a",{"class":"paginate_button current"}).text=="15":
            driver.quit()
            driver1.quit()

            break
   

   

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


