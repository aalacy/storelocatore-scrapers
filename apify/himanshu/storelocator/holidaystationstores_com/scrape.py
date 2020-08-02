import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code","store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    driver = SgSelenium().firefox()
    base_url = "https://www.holidaystationstores.com/"
    data = {"Lat": 40.4172871,
            "Lng": -82.90712300000001,
            "Diesel": "false",
            "E85": "false",
            "NonOxygenated": "false",
            "Carwash": "false",
            "UnlimitedCarWashPass": "false",
            "Open24Hours": "false",
            "ATM": "false",
            "Cub": "false",
            "UnattendedFueling": "false",
            "TruckStop": "false",
            "DEF": "false",
            "Propane": "false",
            "CNG": "false",
            "SearchMethod": "City",
            "SearchValue": "OH"
            }

    headers = {
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,gu;q=0.8,es;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    r = session.post("https://www.holidaystationstores.com/Locations/Results/", data=data, headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for name in soup.find_all("a",{"class":"HolidayHoverNone"}):
        location_name = name.find("div",{"class":"col-12 HolidayFontColorRedHover font-weight-bold"}).text.strip()
        store_number = location_name.split("#")[-1]
        longitude = name['data-lng']
        latitude = name['data-lat']
        street_address = name.find_all("div")[1].text
        raw = name.find_all("div")[-1].text
        city = raw.split(",")[0]
        state = raw.split(",")[1].split()[0]
        zipp = raw.split(",")[1].split()[1]
        page_url = "http://www.holidaystationstores.com/Locations/Detail?storeNumber="+str(store_number)
        driver.get(page_url)
        location_soup = BeautifulSoup(driver.page_source, "lxml")
        phone = location_soup.find("div",{"class":"col-lg-4 col-sm-12"}).find("div",{"class":"HolidayFontColorRed"}).text.strip()
        hours = " ".join(list(location_soup.find("div",{"class":"col-lg-4 col-sm-12"}).stripped_strings)).split("Hours")[1].split("Services")[0].strip()
    
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude )
        store.append(longitude )
        store.append(hours)
        store.append(page_url)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        #print(store)
        yield store

    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
