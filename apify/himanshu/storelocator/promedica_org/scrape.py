import csv
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import platform
system = platform.system()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = requests.post(url,headers=headers,data=data)
                else:
                    r = requests.post(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None


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
    driver = get_driver()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    base_url = "https://www.promedica.org"
    addresses = []

    # driver.get('https://www.promedica.org/Pages/OHAM/OrgUnitsSearchResult.aspx?Radius=-1&IncludeChildUnits=1&IncludeLinkedUnits=0&IncludeCurrent=True&RadiusUnit=Miles&PostalCodeControlHidden=False&RadiusControlHidden=False&RadiusUnitDefault=Any%20Distance&RadiusLabelText=Search%20Within&TypeIds=0')
    driver.get('https://www.promedica.org/Pages/OHAM/OrgUnitsSearchResult.aspx')


    isLast = False
    while not isLast:
        soup = BeautifulSoup(driver.page_source,"lxml")
        for loc_detail in soup.find_all("a",{"class":"location-search-results"}):

            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = "US"
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            raw_address = ""
            hours_of_operation = ""
            page_url = ""

            # do your logic here.
            page_url = loc_detail["href"]
            # page_url = 'https://www.promedica.org/Pages/OHAM/OrgUnitDetails.aspx?OrganizationalUnitId=135'
            # print("page_url = ",page_url)
            r_location = request_wrapper(page_url,"get", headers=headers)
            soup_location = BeautifulSoup(r_location.text, "lxml")
            if soup_location.find("h1",{"class":"loc-top-image"}):
                # store_number = loc_detail.find("OrganizationID").next
                full_address = list(soup_location.find("div",{"class":"address-block xs-mbm"}).find("a").stripped_strings)
                # print("full_address == ", full_address)
                if len(full_address) > 1:
                    location_name = soup_location.find("h1",{"class":"loc-top-image"}).text
                    phone = soup_location.find("a",{"class":"phone"}).text
                    street_address = ", ".join(full_address[:-1])
                    if "Suite" in street_address:
                        street_address = "".join(street_address[:street_address.index("Suite")])
                    ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address[-1]))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address[-1]))

                    if ca_zip_list:
                        zipp = ca_zip_list[-1]
                        country_code = "CA"

                    if us_zip_list:
                        zipp = us_zip_list[-1]
                        country_code = "US"

                    city = full_address[-1].split(",")[0]
                    state = full_address[-1].split(",")[1].strip().split(" ")[0]
                    latitude = soup_location.text.split("Latitude:'")[1].split("'")[0]
                    longitude = soup_location.text.split("Longitude:'")[1].split("'")[0]

                    tag_hours = soup_location.find(lambda tag: (tag.name == "h2") and "Hours of Operation" == tag.text.strip()).parent
                    if tag_hours:
                        hours_of_operation = ", ".join(list(tag_hours.stripped_strings)[1:])

                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                    if str(store[2]) not in addresses and country_code:
                        addresses.append(str(store[2]))

                        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                        # print("data = " + str(store))
                        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        yield store

        if soup.find("input",{"class":"rdpPageNext","onclick":True}):
            isLast = True
        else:
            driver.find_element_by_xpath("//input [@class='rdpPageNext']").click()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
