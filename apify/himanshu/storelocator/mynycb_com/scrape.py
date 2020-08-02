import csv
import requests
from bs4 import BeautifulSoup
from sgselenium import SgSelenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import re
import unicodedata
import sgzip


def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    driver = SgSelenium().firefox()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    addresses = []
    coords = sgzip.coords_for_radius(200)
    for coord in coords:
        x = coord[0]
        y = coord[1]
        # print("https://www.mynycb.com/Pages/Location-Search-Results.aspx?lat="+ str(x) + "&long=" + str(y) + "&r=200")
        # url = ''

        driver.get("https://www.mynycb.com/Pages/Location-Search-Results.aspx?lat="+ str(x) + "&long=" + str(y) + "&r=200")
        try:
            WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath("//p[text()='No Results Found']"))
            continue
        except:
            pass
        try:
            WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath("//div[@class='row']"))
        except:
            continue
        # print(driver.find_element_by_xpath("//div[@class='row']").get_attribute('value'))
        while True:
            soup = BeautifulSoup(driver.page_source,'lxml')
            geo_script = ""
            for script in soup.find_all("script"):
                if "google.maps.Marker({" in script.text:
                    geo_script = script.text
                    break
            if soup.find("div",{"class":"atmBranchResultsWP"}) == None:
                break
            for location in soup.find("div",{"class":"atmBranchResultsWP"}).find_all("div",{"class":"row"}):
                if location.find("div",{"class":"aLocationID"}) == None:
                    continue
                store_id = " ".join(list(location.find("div",{"class":"aLocationID"}).stripped_strings))
                lat = geo_script.split("var marker"+str(store_id))[1].split("LatLng(")[1].split(",")[0]
                lng = geo_script.split("var marker"+str(store_id))[1].split("LatLng(")[1].split(",")[1].split(")")[0]
                name = " ".join(list(location.find("div",{"class":"name"}).stripped_strings))
                address = list(location.find("div",{"class":"address"}).stripped_strings)
                store = []
                store.append("https://www.mynycb.com")
                store.append(name)
                store.append(" ".join(address[:-1]))
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(address[-1].split(",")[0])
                if store[-1] == "":
                    store[-1] = "<MISSING>"
                state_split = re.findall("([A-Z]{2})",address[-1])
                if state_split:
                    state = state_split[-1]
                else:
                    state = "<MISSING>"
                store_zip_split = re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",address[-1])
                if store_zip_split:
                    store_zip = store_zip_split[-1]
                else:
                    store_zip = "<MISSING>"
                store.append(state  if state else "<MISSING>")
                store.append(store_zip if store_zip else "<MISSING>")
                store.append("US")
                store.append(store_id)
                if location.find("div",{'class':"phone"}):
                    phone = " ".join(list(location.find("div",{'class':"phone"}).stripped_strings)).replace("Phone:","")
                else:
                    phone = "<MISSING>"
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat)
                store.append(lng)
                hours = " ".join(list(location.find("div",{"class":"aLocationHours"}).stripped_strings))
                store.append(hours if hours and hours != "ATM Only at this location" else "<MISSING>")
                store.append("<MISSING>")
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                # print(store)
                yield store
            if soup.find("a",text="Next") == None:
                break
            if soup.find("a",{"class":"aspNetDisabled"},text="Next"):
                break
            driver.find_element_by_xpath("//a[text()='Next']").click()
     

def scrape():
    data = fetch_data()
    write_output(data)

scrape()