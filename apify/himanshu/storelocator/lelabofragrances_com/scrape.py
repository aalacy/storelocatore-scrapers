import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
import time
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    driver = SgSelenium().firefox()
    adressess = []
    base_url = "https://www.lelabofragrances.com"
    driver.get('https://www.lelabofragrances.com/front/app/store/search')
    driver.find_element_by_xpath("//div[@class='selectize-input items has-options full has-items']").click()
    driver.find_element_by_xpath("//div[@data-value='US']").click()
    driver.find_element_by_xpath("//button[@type='submit']").click()
    driver.find_element_by_xpath("//a[@class='locations-toggle-btn tablet-hidden']").click()
    driver.find_element_by_xpath('//*[@id="location-links"]/ul/li[1]/a').click()
    soup = BeautifulSoup(driver.page_source,"lxml")
    for location in soup.find_all("li",{"class":"store-country-US"}):
        location_name = location.find("div",{"class":"store-name"}).text.strip()
        rm = ["SEOUL - SHINSEGAE GANGNAM DUTY FREE",
        "SEOUL - HYUNDAI DUTY FREE","WELLINGTON - MECCA WELLINTON",
        "AUCKLAND - MECCA COSMETICA TAKAPUNA",
        "AUCKLAND - MECCA COSMETICA NEWMARKET",
        "AUCKLAND - MECCA AUCKLAND",
        "SEOUL - SHILLA I-PARK DUTY FREE",
        "BELGRADE - METROPOLITEN",
        "CHRISTCHURCH - MECCA COSMETICA BALLANTYNES"]
        if location_name in rm:
            continue
        add = list(location.find("div",{"class":"store-address"}).stripped_strings)
        if len(add)==2:
            street_address = add[0]
            addr = add[1].split(",")
            if len(addr)==4:
                city = addr[0]
                state = addr[2].strip().split(" ")[0]
                zipp = addr[2].strip().split(" ")[1]
            else:
                city = addr[0]
                state = addr[1].strip().split(" ")[0]
                zipp = addr[1].strip().split(" ")[1]
        else:
            street_address = ", ".join(add[:2])
            addr = add[2].split(",")
            city = addr[0]
            state = addr[1].strip().split(" ")[0]
            zipp = addr[1].strip().split(" ")[1]
        if len(zipp)==4:
            zipp = "0"+zipp
        if zipp=="11430":
            phone = "<MISSING>"
        phone = location.find("div",{"class":"store-number"}).text.replace("ph:","").strip()
        if phone=="0":
            phone = "<MISSING>"
        try:
            hours_of_operation = ",".join(list(location.find("div",{"class":"store-hours"}).stripped_strings))
            if hours_of_operation=="Temporarily closed.":
                hours_of_operation = "<MISSING>"
        except:
            hours_of_operation = "<MISSING>"
        if hours_of_operation=="Closed.":
            continue
        hours_of_operation = hours_of_operation.replace("Temporarily closed.,","")
        street_address = street_address.replace(", The Shops at Riverside","").replace(", Westfield Topanga","").replace(", The Americana at Brand","").replace(", The Shops at North Bridge","").replace(", Oakbrook Center","").replace(", Broadway Plaza","")
        store = []
        store.append("https://www.lelabofragrances.com")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone.strip() else "<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append("<MISSING>")
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in adressess:
            continue
        adressess.append(store[2])
        yield store
    time.sleep(10)
    driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[2]/div/div/div/div[1]/a[1]").click()
    driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[2]/div/div/div/div[1]/a[1]").click()
    driver.find_element_by_xpath('//*[@id="location-links"]/ul/li[5]/a').click()
    soup = BeautifulSoup(driver.page_source,"lxml")
    for location in soup.find_all("li",{"class":"store-country-CA"}):
        location_name = location.find("div",{"class":"store-name"}).text.strip()
        add = list(location.find("div",{"class":"store-address"}).stripped_strings)
        if len(add)==2:
            street_address = add[0]
            addr = add[1].split(",")
            city = addr[0]
            state = addr[1].strip().split(" ")[0]
            zipp = " ".join(addr[1].strip().split(" ")[1:])
        else:
            if location_name=="VANCOUVER INTERNATIONAL AIRPORT - INTERNATIONAL TERMINAL":
                street_address = add[1]
            else:
                street_address = add[0]
            addr = add[-1].split(",")
            city = addr[0]
            state = addr[1].strip().split(" ")[0]
            zipp = " ".join(addr[1].strip().split(" ")[1:])
        phone = location.find("div",{"class":"store-number"}).text.replace("ph: +1","").strip()
        try:
            hours_of_operation = ",".join(list(location.find("div",{"class":"store-hours"}).stripped_strings))
            if hours_of_operation=="Temporarily closed.":
                hours_of_operation = "<MISSING>"
        except:
            hours_of_operation = "<MISSING>"
        store = []
        store.append("https://www.lelabofragrances.com")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("CA")
        store.append("<MISSING>")
        store.append(phone if phone.strip() else "<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append("<MISSING>")
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()