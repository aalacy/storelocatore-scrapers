import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
from selenium.webdriver.support.wait import WebDriverWait
import time
import html


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    r = session.get("http://www.crosbysmarkets.com/?page_id=14")
    main_soup = BeautifulSoup(r.text,"lxml")
    iframe_link = main_soup.find("iframe")["src"]
    r = session.get(iframe_link)
    soup = BeautifulSoup(r.text,"lxml")
    geo_location = {}
    for script in soup.find_all("script"):
        if "_pageData" in script.text:
            location_list = json.loads(script.text.split('var _pageData = "')[1].split('\n";')[0].replace('\\"','"').replace(r"\n","")[:-2].replace("\\"," "))[1][6] # [0][12][0][13][0]
            for location in location_list:
                geo_location[location[2].replace(" u0027s","'s")] = location[4][0][4][0][1]
    hours = " ".join(list(main_soup.find("b",text=re.compile("Store Hours")).parent.stripped_strings)).replace("\n","").replace("\r","")
    driver = SgSelenium().firefox()
    addresses = []
    driver.get(iframe_link)
    time.sleep(3)
    driver.find_element_by_xpath("//div[@class='i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c']").click()
    for button in driver.find_elements_by_xpath("//*[contains(text(), '...')]"):
        time.sleep(1)
        button.click()
    count = 0
    for button in driver.find_elements_by_xpath("//div[contains(@index, '')]"):
        try:
            if button.get_attribute("index") == None:
                continue
            name_soup = BeautifulSoup(driver.page_source,"lxml")
            index = str(button.get_attribute("index"))
            name = name_soup.find_all("div",{"index":index})[count].parent.parent.find("label").text.strip()
            count = count + 1
            time.sleep(1)
            button.click()
            time.sleep(2)
            location_soup = BeautifulSoup(driver.page_source, "lxml")
            # name = list(location_soup.find("div",text=re.compile("name")).parent.stripped_strings)[1]
            address = list(location_soup.find("div",text=re.compile("Details from Google Maps")).parent.stripped_strings)[1]
            street_address = address.split(",")[0]
            city = address.split(",")[1]
            store_zip_split = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),address)
            if store_zip_split:
                store_zip = store_zip_split[-1]
            else:
                store_zip = "<MISSING>"
            state_split = re.findall("([A-Z]{2})",address)
            if state_split:
                state = state_split[-1]
            else:
                state = "<MISSING>"
            if location_soup.find("div",text=re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")):
                phone = location_soup.find("div",text=re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")).text
            else:
                phone = "<MISSING>"
            store = []
            store.append("http://www.crosbysmarkets.com/")
            store.append(name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(store_zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(geo_location[name][0])
            store.append(geo_location[name][1])
            store.append(hours.strip() if hours else "<MISSING>")
            store.append("<MISSING>")
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            #print(store)
            yield store
            time.sleep(2)
            driver.find_element_by_xpath("//span[@class='HzV7m-tJHJj-LgbsSe-Bz112c qqvbed-a4fUwd-LgbsSe-Bz112c']").click()
        except Exception as e:
            print(e)
            time.sleep(1)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
