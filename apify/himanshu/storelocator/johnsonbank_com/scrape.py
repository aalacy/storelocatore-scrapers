import csv
import time
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 10
    addresses123 =[]
    store_detail=[]
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Content-type': 'application/x-www-form-urlencoded'
    }

    base_url = "https://www.johnsonbank.com"

    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]

        # lat = 43.42409374556526
        # lng = -73.71329370598734
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        location_url = "https://johnsonbank.locatorsearch.com/GetItems.aspx"
        try:
            r = requests.post(location_url, headers=headers, data="lat=" + str(lat) + "&lng=" + str(
                lng) + "&searchby=FCS%7CDRIVEUP%7CDRIVEUPATM%7CATMSF%7C")
        except :
            continue

        try:
            r1 = requests.post(location_url, headers=headers, data="lat=" + str(lat) + "&lng=" + str(
                lng) + "&searchby=ATMSF%7C&SearchKey=&rnd=1575264836020")
        except :
            continue


        soup = BeautifulSoup(r.text, "html.parser")
        soup1 = BeautifulSoup(r1.text, "html.parser")
        current_results_len = len(soup.find_all("marker")+soup1.find_all("marker"))
        
        for script in soup1.find_all("marker"):
            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = "CA"
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            raw_address = ""
            page_url = ""
            hours_of_operation = ""

            # do your logic here

            title_tag = BeautifulSoup(script.find("title").text,"html.parser").find("a")
            if title_tag:
                page_url = "https://johnsonbank.locatorsearch.com/"+title_tag["href"]

            location_name = script.find("label").text
            street_address = script.find("add1").text
            latitude = script["lat"]
            longitude = script["lng"]
            list_address = list(script.find("add2").stripped_strings)

            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_address))
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(list_address))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(list_address))
            state_list = re.findall(r' ([A-Z]{2}) ', str(list_address))

            # print("script == " + str(list_address))
            if phone_list:
                phone = phone_list[0]

            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"

            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"

            if state_list:
                state = state_list[-1]

            city = list_address[0].split(",")[0]

            if script.find("contents"):
                hours_soup = BeautifulSoup(script.find("contents").text,"html.parser")
                if hours_soup.find("div",{"class":"infowindow"}) and hours_soup.find("table"):
                    hours_of_operation = " ".join(list(hours_soup.find("div",{"class":"infowindow"}).stripped_strings))
                    # print("hours_list === "+ str(hours_of_operation))

            result_coords.append((latitude, longitude))
            store1 = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            store_detail.append(store1)

            # if str(store1[2]) + str(store1[-3]) not in addresses123:
            #     addresses123.append(str(store1[2]) + str(store1[-3]))

            #     store1 = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store1]

            #     print("data = " + str(store1))
            #     print('~~~~~~~~~~~~~~~~~~~~~~~~store1~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            #     yield store1
            
        
        # print("soup === " + str(soup))
        # print("current_results_len === " + str(current_results_len))

        for script in soup.find_all("marker"):

            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = "CA"
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            raw_address = ""
            page_url = ""
            hours_of_operation = ""

            # do your logic here

            title_tag = BeautifulSoup(script.find("title").text,"html.parser").find("a")
            if title_tag:
                page_url = "https://johnsonbank.locatorsearch.com/"+title_tag["href"]

            location_name = script.find("label").text
            street_address = script.find("add1").text
            latitude = script["lat"]
            longitude = script["lng"]

            list_address = list(script.find("add2").stripped_strings)

            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_address))
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(list_address))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(list_address))
            state_list = re.findall(r' ([A-Z]{2}) ', str(list_address))

            # print("script == " + str(list_address))
            if phone_list:
                phone = phone_list[0]

            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"

            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"

            if state_list:
                state = state_list[-1]

            city = list_address[0].split(",")[0]

            if script.find("contents"):
                hours_soup = BeautifulSoup(script.find("contents").text,"html.parser")
                if hours_soup.find("div",{"class":"infowindow"}) and hours_soup.find("table"):
                    hours_of_operation = " ".join(list(hours_soup.find("div",{"class":"infowindow"}).stripped_strings))
                    # print("hours_list === "+ str(hours_of_operation))

            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store_detail.append(store)
            # if str(store[2]) + str(store[-3]) not in addresses:
            #     addresses.append(str(store[2]) + str(store[-3]))

            #     store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            #     print("data = " + str(store))
            #     print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            #     yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

    for q in range(len(store_detail)):
        if store_detail[2] in addresses:
            continue
        addresses.append(store_detail[2])
        yield store_detail[q]






def scrape():
    data = fetch_data()
    write_output(data)


scrape()
