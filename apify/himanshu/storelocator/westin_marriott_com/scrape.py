import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from shapely.prepared import prep
from shapely.geometry import Point
from shapely.geometry import mapping, shape
from sgselenium import SgSelenium
from selenium.webdriver.support.wait import WebDriverWait
import time
import unicodedata


session = SgRequests()

countries = {}
   

def getcountrygeo():
    data = session.get("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson").json()

    for feature in data["features"]:
        geom = feature["geometry"]
        country = feature["properties"]["ADMIN"]
        countries[country] = prep(shape(geom))


def getplace(lat, lon):
    if lon != "" and lat != "":
        point = Point(float(lon), float(lat))
    else:
        point = Point(0, 0)
        # print("lat == ",lat,"lng == ",lon)
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    
    for country, geom in countries.items():
        if geom.contains(point):
            return country

    return "unknown"

def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    getcountrygeo()
    driver = SgSelenium().firefox()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    addresses = []
    brand_id = "WI"
    domain_url = "https://westin.marriott.com"
    # driver.get("https://westin.marriott.com/hotel-locations/")
    # wait = WebDriverWait(driver, 10)
    # element = wait.until(lambda x: x.find_element_by_xpath("//a[text()='View all hotels']"))
    # element.click()
    driver.get("https://www.marriott.com/search/submitSearch.mi?showMore=true&marriottBrands=" + str(brand_id) + "&destinationAddress.country=US")
    element = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//input[@id="keywords"]'))
    element.send_keys("westin") 
    WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//input[@value="Search Hotels"]')).click()
    while True:
        # wait = WebDriverWait(driver, 10)
        # element = wait.until(lambda x: x.find_element_by_xpath("//div[text()='Destination']"))
        soup = BeautifulSoup(driver.page_source,"lxml")
 
        for location in soup.find('div',{'class':'js-property-list-container'}).find_all("div",{"data-brand":str(brand_id)},recursive=False):
            if location["data-brand"] != brand_id:
                continue
            lat = json.loads(location["data-property"])["lat"]
            lng = json.loads(location["data-property"])["longitude"]
            country_name = getplace(lat, lng)
            if country_name not in ["United States of America","Canada"]:
                continue
            #print(country_name)
            
            name = location.find("span",{"class":"l-property-name"}).text
            address = location.find("div",{"data-address-line1":True})
            street_address = address["data-address-line1"]
            if location.find("div",{"data-address-line2":True}):
                street_address = street_address + " " + address["data-address-line2"]
            city = address["data-city"]
            state = address["data-state"]
            if state in ["QROO","JAL","DF","NL"]:
                continue
            store_zip = address["data-postal-code"]
            phone = address["data-contact"]
            
            page_url = "https://www.marriott.com" + location.find("span",{"class":"l-property-name"}).parent.parent["href"]
            store = []
            store.append(domain_url)
            store.append(name if name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            if store[-1] == "":
                continue
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(store_zip))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(store_zip))
            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"

            elif us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"
            else:
                continue
            store.append(zipp if zipp else "<MISSING>")
            if len(store[-1]) == 10:
                store[-1] = store[-1].replace(" ","-")
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append("<MISSING>")
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
            # print("data === ",str(store))
        # if len(soup.find('div',{'class':'js-property-list-container'}).find_all("div",{"data-brand":str(brand_id)})) <= 0:
        #     break
        soup = BeautifulSoup(driver.page_source,"lxml")

        if soup.find("a",{"title":"Next"}):
            driver.find_element_by_xpath("//a[@title='Next']").click()
        else:
            break
    driver.close()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
