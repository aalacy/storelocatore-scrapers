import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from selenium.webdriver.support.wait import WebDriverWait
import platform

system = platform.system()


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


    # print("start")
    base_url = "https://www.mynycb.com"
    addresses = []
    driver = get_driver()
    driver.get("https://www.autozone.com/locations/")
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source,"xml")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    store_name=[]
    store_detail=[]
    return_main_object=[]

    k= soup.find_all("li",{"class":"c-directory-list-content-item"})
    for i in k:
        link = i.text.split("(")[-1]
        if link != "1)":
            # print("-----------------------",i.find("a"))
            city_link = "https://www.autozone.com/locations/"+i.find("a")['href']
            driver.get(city_link)
            time.sleep(2)
            # ,headers=headers
            soup1 = BeautifulSoup(driver.page_source,"xml")
            # print('rrrrrrrrrrrrrrrrrrrrrr ',soup1)
            citylink= soup1.find_all("li",{"class":"c-directory-list-content-item"})
            for c in citylink:
                link1 = c.text.split("(")[-1]
                if link1 != "1)":
                    # print(c.find("a")['href'])
                    sublink = "https://www.autozone.com/locations/"+c.find("a")['href']
                    driver.get(sublink)
                    time.sleep(2)
                    soup2 = BeautifulSoup(driver.page_source,"xml")
                    store_link = soup2.find_all("h5",class_="c-location-grid-item-title")
                    for st in store_link:
                        # print(st.find("a")['href'].replace("..",""))
                        # r3 = requests.get("https://locations.checkers.com"+st['href'].replace("..",""))
                        page_url = "https://www.autozone.com/locations"+st.find("a")['href'].replace("..","")
                        driver.get(page_url)
                        time.sleep(2)
                        soup3 = BeautifulSoup(driver.page_source,"xml")
                        streetAddress = soup3.find("span",{"class":"c-address-street-1"}).text.strip()
                        state = soup3.find("abbr",{"class":"c-address-state"}).text
                        zip1 = soup3.find("span",{"class":"c-address-postal-code"}).text
                        city = soup3.find("span",{"class":"c-address-city"}).text
                        name = " ".join(list(soup3.find("h1",{"class":"c-location-title"}).stripped_strings))
                        phone = soup3.find("span",{"class":"c-phone-number-span c-phone-main-number-span"}).text
                        hours = " ".join(list(soup3.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
                        latitude = soup3.find("meta",{"itemprop":"latitude"})['content']
                        longitude = soup3.find("meta",{"itemprop":"longitude"})['content']
                        
                        tem_var =[]
                        tem_var.append("https://www.autozone.com")
                        tem_var.append(name)
                        tem_var.append(streetAddress)
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zip1)
                        tem_var.append("US")
                        tem_var.append("<MISSING>")
                        tem_var.append(phone)
                        tem_var.append("<MISSING>")
                        tem_var.append(latitude)
                        tem_var.append(longitude)
                        tem_var.append(hours)
                        tem_var.append(page_url)
                        yield tem_var
                        # print("========================================",tem_var)

                else:
                    one_link = "https://www.autozone.com/locations/"+c.find("a")['href']
                    page_url = one_link
                    driver.get(one_link)
                    time.sleep(2)
                    soup4 = BeautifulSoup(driver.page_source,"xml")
                    streetAddress = soup4.find("span",{"class":"c-address-street-1"}).text.strip()
                    state = soup4.find("abbr",{"class":"c-address-state"}).text
                    zip1 = soup4.find("span",{"class":"c-address-postal-code"}).text
                    city = soup4.find("span",{"class":"c-address-city"}).text
                    name = " ".join(list(soup4.find("h1",{"class":"c-location-title"}).stripped_strings))
                    phone = soup4.find("span",{"class":"c-phone-number-span c-phone-main-number-span"}).text
                    hours = " ".join(list(soup4.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
                    latitude = soup4.find("meta",{"itemprop":"latitude"})['content']
                    longitude = soup4.find("meta",{"itemprop":"longitude"})['content']

                    tem_var =[]
                    tem_var.append("https://www.autozone.com")
                    tem_var.append(name)
                    tem_var.append(streetAddress)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("<MISSING>")
                    tem_var.append(latitude)
                    tem_var.append(longitude)
                    tem_var.append(hours)
                    tem_var.append(page_url)
                    yield tem_var
                    # print("========================================",tem_var)
        else:
            one_link1 = "https://www.autozone.com/locations/"+i.find("a")['href']
            page_url = one_link1
            driver.get(page_url)
            time.sleep(2)
            soup5 = BeautifulSoup(driver.page_source,"xml")

            streetAddress = soup5.find("span",{"class":"c-address-street-1"}).text.strip()
            state = soup5.find("abbr",{"class":"c-address-state"}).text
            zip1 = soup5.find("span",{"class":"c-address-postal-code"}).text
            city = soup5.find("span",{"class":"c-address-city"}).text
            name = " ".join(list(soup5.find("h1",{"class":"c-location-title"}).stripped_strings))
            phone = soup5.find("span",{"class":"c-phone-number-span c-phone-main-number-span"}).text
            hours = " ".join(list(soup5.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
            latitude = soup5.find("meta",{"itemprop":"latitude"})['content']
            longitude = soup5.find("meta",{"itemprop":"longitude"})['content']
            # print(streetAddress)
            tem_var =[]
            tem_var.append("https://www.autozone.com/")
            tem_var.append(name)
            tem_var.append(streetAddress)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hours)
            tem_var.append(page_url)
            yield tem_var
            # print("========================================",tem_var)
    



def scrape():
    data = fetch_data()
    write_output(data)


scrape()


