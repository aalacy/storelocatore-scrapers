import csv
import time
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        
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
    addressess=[]
    store_detail=[]
    current_results_len = 0  
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
            page_url = "<MISSING>"
            hours_of_operation = ""


            title_tag = BeautifulSoup(script.find("title").text,"html.parser").find("a")
            if title_tag:
                page_url = "https://johnsonbank.locatorsearch.com/"+title_tag["href"]
           
            location_name = script.find("label").text.strip().lstrip().replace("                  ",'').replace("        ","").replace("     ","").replace("    ","")
            

            street_address = script.find("add1").text
            latitude = script["lat"]
            longitude = script["lng"]
            
            list_address = list(script.find("add2").stripped_strings)
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_address))
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(list_address))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(list_address))
            state_list = re.findall(r' ([A-Z]{2}) ', str(list_address))

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
                        
            

            result_coords.append((latitude, longitude))
          

            store=[]
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append("<MISSING>")
            store.append(phone_list if phone_list else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
            store.append(page_url)
            #print(store)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store


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
            page_url = "<MISSING>"
            hours_of_operation = ""


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
                    
            result_coords.append((latitude, longitude))

            store=[]
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append("<MISSING>")
            store.append(phone_list if phone_list else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
            store.append(page_url)
            #print(store)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store
            

        if current_results_len < MAX_RESULTS:
    
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:

            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

    
      

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
