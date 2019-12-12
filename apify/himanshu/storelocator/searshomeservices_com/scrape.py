import csv
import time
import requests
from bs4 import BeautifulSoup
import re
import json


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

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    addresses = []
    base_url = "http://www.searshomeservices.com"

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

    r = requests.get("https://www.searshomeservices.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for script_state in soup.find_all("a", {"class": "state"}):

        location_state_url = base_url + script_state["href"]
        
        # print("state_location_url === " + str(location_state_url))

        # while True:
        #     try:
        #         r_state_location = requests.get(location_state_url, headers=headers)
        #         break
        #     except Exception as e:
        #         # print("State Error = "+ str(e))
        #         time.sleep(10)
        #         continue
        
        r_state_location = request_wrapper(location_state_url,"get", headers=headers)
        # print(r_state_location)
        if r_state_location == None:
            continue

        soup_state_location = BeautifulSoup(r_state_location.text, "lxml")

        for script_store in soup_state_location.find_all("div", {"class": "state-store-item state-store-item-default"}):

            if "http" in script_store.find("a")["href"]:
                page_url = script_store.find("a")["href"]
            else:
                page_url = base_url + script_store.find("a")["href"]

            # print("location_url === " + str(page_url))

            # while True:
            #     try:
            #         r_store_detail = requests.get(page_url, headers=headers)
            #         break
            #     except Exception as e:
            #         # print("Store Error = "+ str(e))
            #         time.sleep(10)
            #         continue

            r_store_detail = request_wrapper(page_url,"get", headers=headers)

            if r_store_detail == None:
                continue

            soup_store_detail = BeautifulSoup(r_store_detail.text, "lxml")

            if soup_store_detail.find("span",{"class":"store-hours"}):
                hours_of_operation = " ".join(list(soup_store_detail.find("span",{"class":"store-hours"}).stripped_strings)).replace('Hours','').strip()
            else:
                hours_of_operation = ""

            try:
                json_str = (soup_store_detail.text.split("config.currentStore = ")[1]+"{").split("}]};")[0]+"}]}"
                json_data = json.loads(json_str)

                street_address = str(json_data["address"])
                location_name = str(json_data["location_name"])
                # print(location_name)
                city = str(json_data["city"])
                state = str(json_data["state"])
                zipp = str(json_data["zip"])
                phone = str(json_data["phone"])
                store_number = str(json_data["id"])
                latitude = str(json_data["lat"])
                longitude = str(json_data["long"])
                location_type = str(json_data["location_type"])

                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))

                country_code = ""
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country_code = "CA"

                if us_zip_list:
                    zipp = us_zip_list[-1]
                    country_code = "US"
            except:
                if "metro-area" not in page_url :
                    head= soup_store_detail.find('div',class_='headerMain-utilZone03')
                    if head != None:
                        
                        city = head.find('span',{'itemprop':'addressLocality'}).text.strip()
                        state = head.find('span',{'itemprop':'addressRegion'}).text.strip()
                        phone = head.find('nav',{'class':'navCallout'}).find('a')['href'].replace('tel:','').strip()
                        location_name = city
                        street_address = "<MISSING>"
                        zipp = "<MISSING>"
                        location_type = "<MISSING>"
                        store_number = "<MISSING>"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        country_code = "US"
                        page_url = page_url

                    else:
                        #this page has no detail information 
                        continue
                        # print(page_url)

                        

                else:
                    # this pages have duplicate location 
                    continue


                

            

            # print("hours_of_operation == "+ str(store_number))

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[1]) + str(store[2]) not in addresses and country_code:
                addresses.append(str(store[1]) + str(store[2]))

                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
