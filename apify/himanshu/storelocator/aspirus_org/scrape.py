import csv
from bs4 import BeautifulSoup
import requests
from sgrequests import SgRequests
import time
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import platform
system = platform.system()


session = SgRequests()
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


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8",newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
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

def fetch_data():
    
    
     # it will used in store data.
    addresses = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.aspirus.org"
    locator_domain = base_url
    r = request_wrapper("https://www.aspirus.org/find-a-location","get", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    key_add_list = []
    lat_list =[]
    lng_list = []
    
    for loc_type_soup in soup.find("div", {"class": "locations"}).find_all("div",{"class","view-all1"}):

        locator_domain = base_url
        location_type = ""

    #     # do your logic here.
        location_type = loc_type_soup.find("a").find("strong").text
        loc_type_url = base_url + loc_type_soup.find("a")["href"]

        r_loc_list = request_wrapper(loc_type_url,"get", headers=headers)
        soup_loc_list = BeautifulSoup(r_loc_list.text, "lxml")

        split_latlng = r_loc_list.text.split("myLatlng = new google.maps.LatLng(")
        map_latlng = {}
        
        for str_data in split_latlng[1:]:
            final_data = str_data.split("});")[0]
            key_address = final_data.split("</strong><br />")[1].split("<br />")[0].strip()
            key_add_list.append(key_address)
            if key_address not in map_latlng:
                map_latlng[key_address] = {}
            map_latlng[key_address]["latitude"] = final_data.split(",")[0]
            lat_list.append(map_latlng[key_address]["latitude"])
            map_latlng[key_address]["longitude"] = final_data.split(",")[1].split(")")[0]
            lng_list.append(map_latlng[key_address]["longitude"])
            # print(map_latlng[key_address]["latitude"],map_latlng[key_address]["longitude"])
    
    
    driver = get_driver()
    driver.get("https://www.aspirus.org/find-a-location?taxonomy=adult-living-care-facilities")
    WebDriverWait(driver, 10).until(
                lambda x: x.find_element_by_xpath("//input[@id='cpsys_FormItem_moduleSearch_moduleSearchBtn']")).click()
    
    page=2
    vk=10
    while True:
        # print(driver.current_url)
        
        soup_loc_list  =BeautifulSoup(driver.page_source,"lxml")
        if soup_loc_list.find("ul", {"class": "results"}):

            for location in soup_loc_list.find("ul", {"class": "results"}).find_all("li",{"data-loc":True}):
                
                location_name = ""
                street_address = ""
                city = ""
                state = ""
                zipp = ""
                country_code = "US"
                store_number = ""
                phone = ""
                location_type ="<MISSING>"
                latitude = ""
                longitude = ""
                raw_address = ""
                hours_of_operation = ""
                page_url = ""

                page_url = base_url + location.find("a")["href"]
                # print("page_url : ",page_url)
                # print("//a[@id='cphBody_cphCenter_ctl01_PaginationTop_PaginationTop_lb']")
                page_v="Page "+str(page)
                # print(page_v)
                r_location = request_wrapper(page_url,"get", headers=headers)
                soup_location = BeautifulSoup(r_location.text, "lxml")

                full_address = list(soup_location.find("ul",{"class":"gen-info flex"}).stripped_strings)

                location_name = full_address[1]
                street_address = full_address[2].strip()
                
                for i in range(len(key_add_list)):
                    if street_address == key_add_list[i]:
                        latitude = lat_list[i]
                        longitude = lng_list[i]
                street_address = full_address[2].split(",")[0].strip()
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(full_address))
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address))
                state_list = re.findall(r'\b[A-Z]{2}\b', str(full_address))

                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country_code = "CA"

                if us_zip_list:
                    zipp = us_zip_list[-1]
                    country_code = "US"

                if state_list:
                    state = state_list[-1]

                if phone_list:
                    phone = phone_list[-1]
                map_it_index = full_address.index("Map It")
                city = full_address[:map_it_index][-1].split(",")[0].strip()
                # print("city == ",str(city))
                # city = city_state_zipp.replace(zipp, "").replace(state, "").replace(",", "")
                if "Hours" in full_address:
                    hours_of_operation = " ".join(full_address[full_address.index("Hours"):]).replace("Hours Business Office Hours","").replace("Hours","").replace("Store","").strip()
                # print("full_address == ",full_address)


                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                if str(str(store[2])+str(store[-1])) not in addresses and country_code:
                    addresses.append(str(store[2])+str(store[-1]))

                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                    # print("data = " + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store
        else:
            break
        time.sleep(10)
        if page > 47:
            break
        if page-1 == vk:
            vk +=10
            driver.find_element_by_xpath("//a[@title='"+str('Next 10')+"']").click()
        time.sleep(10)
        driver.find_element_by_xpath("//a[@title='"+str(page_v)+"']").click()
        
        page += 1
    driver.close()
 
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


