import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import urllib3
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
import platform

system = platform.system()

urllib3.disable_warnings()


# def get_driver():
#     options = Options()
#     # options.add_argument('--headless')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--window-size=1920,1080')
#     return webdriver.Firefox(executable_path='geckodriver.exe', options=options)


# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#     }
# base_url = "https://www.signaturestyle.com"
# r = requests.get("https://kwiktrip.com/Maps-Downloads/Store-List")
# soup = BeautifulSoup(r.text, "lxml" , verify=False)
# print(soup)
                




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    if "linux" in system.lower():
        return webdriver.Firefox(executable_path='./geckodriver', options=options)        
    else:
        return webdriver.Firefox(executable_path='geckodriver.exe', options=options)



def fetch_data():


    addresses = []
    driver = get_driver()
    driver.get("https://kwiktrip.com/Maps-Downloads/Store-List")
    locator_domain = "https://kwiktrip.com"
    
    # print(soup.find_all("table",{"id":"tablepress-4"}))
    while True:
        soup = BeautifulSoup(driver.page_source,"lxml")
        for data in soup.find_all("tbody",{"class":"row-hover"}):
            for tr in data.find_all("tr"):
                store_number = list(tr.stripped_strings)[0]
                location_name = list(tr.stripped_strings)[1]
                street_address = list(tr.stripped_strings)[2]
                city = list(tr.stripped_strings)[3]
                state = list(tr.stripped_strings)[4]
                zipp = list(tr.stripped_strings)[5]
                phone = list(tr.stripped_strings)[6]
                latitude = list(tr.stripped_strings)[7]
                longitude = list(tr.stripped_strings)[8]
                page_url ="<MISSING>"
                location_type = "<MISSING>"
                country_code = "US"
                hours_of_operation = "<MISSING>"
                store =[]
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                yield store
                # print(list(tr.stripped_strings))

        soup1 = BeautifulSoup(driver.page_source,"lxml")
        if soup1.find("a",{"id":"tablepress-4_next"}):
            driver.find_element_by_xpath("//a[@id='tablepress-4_next']").click()
        else:
            break
        if soup1.find("a",{"class":"paginate_button current"}).text=="15":
            driver.quit()
            break
        
    # time.sleep(2)
    # soup = BeautifulSoup(driver.page_source,"xml")

   

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


