import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json
session = SgRequests()
import platform
system = platform.system()
import requests

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
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    addresses = []
    base_url = "https://www.extendedstayamerica.com"
    r = session.get(
        "https://www.extendedstayamerica.com/hotels", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for link in soup.find('table', class_='sm_greytxt').find_all('a'):
        state_url = base_url + link['href']
        r_state = session.get(state_url, headers=headers)
        soup_state = BeautifulSoup(r_state.text, 'lxml')
        for a in soup_state.find('div', class_='links').find_all('a'):
            data_url = base_url + a['href']
            import requests
            import json
            url = data_url

            headers = {
                'cache-control': "no-cache",
                }

            response = requests.request("GET", url, headers=headers)            
            json_data = json.loads(response.text.split('pinList =')[1].split("]};")[0]+']}')
            # print(json_data)
            for loc in json_data["PushPins"]:
                # print(loc)
                locator_domain = "https://www.extendedstayamerica.com"
                latitude = loc['Latitude']
                longitude = loc["Longitude"]
                location_name = loc["HotelName"]
                street_address = loc["Address"]
                city = loc["HotelCity"]
                state = loc["HotelState"]
                zipp = loc["HotelZip"]
                # print(zipp)
                page_url = loc["MinisiteUrl"]
                #print(page_url)
                try:
                    r1 = requests.get(page_url)
                    soup = BeautifulSoup(r1.text,"lxml")
                    data_8 =  (soup.find("script",{ "type":"application/ld+json"}).text)
                    json_data = json.loads(data_8)
                    phone1 = (json_data['telephone'])
                except:
                    r1 = requests.get(page_url)
                    soup = BeautifulSoup(r1.text,"lxml")
                    data_8 =  (soup.find("span",{"class":"lblPhn"}).text)
                    phone1 = data_8
               # print(phone1)
                # exit()
                store_number = loc["HotelId"]
                hours_of_operation = "<MISSING>"
                location_type = "Extended Stay America"
                country_code = "US"
                try:
                    phone_tag = session.get(page_url, headers=headers)
                    soup_phone = BeautifulSoup(phone_tag.text, 'lxml')
                    phone = soup_phone.find(
                        'span', {'id': 'cpd_HotelMiniSite_15_lblHotelPhone'}).text.strip()
                    try:
                        hours = list(soup_phone.find(
                            "span", text="Hours of Operation").parent.stripped_strings)
                        hours_of_operation = " ".join(hours).replace(
                            "Hours of Operation", "").strip()
                        # print(hours_of_operation)
                        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    except Exception as e:
                        hours_of_operation = "<MISSING>"
                        # print(e)
                        # print(page_url)
                        # print("**************************************")
                    # print(phone)
                except:
                    # print(page_url)
                    phone = "<MISSING>"
                # print(phone)
                # print(page_url)
                if "<MISSING>" == hours_of_operation:
                    hours_of_operation = "Open 24 hours a day, seven days a week"
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone1, location_type, latitude, longitude, hours_of_operation, page_url]
                store = ["<MISSING>" if x == "" else x for x in store]
                if store_number in addresses:
                    continue
                addresses.append(store_number)
                # print("data == " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
