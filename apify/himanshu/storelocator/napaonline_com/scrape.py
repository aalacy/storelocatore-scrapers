import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    addresses1 = []
    addresses2 = []
    search = sgzip.ClosestNSearch()    
    search.initialize(country_codes=["US"])
    MAX_RESULTS = 300
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        base_url = "https://www.napaonline.com/"
        try:
            r  = requests.get("https://www.napaautocare.com/store-finder.aspx?zip="+str(zip_code)+"&address=undefined&city=&state=&storetype=Mechanical%20Center&distance="+str(MAX_DISTANCE)+"&filter=undefined&autocareFilter=false&aaaAutoApproved=false&cbCharge=false&sortBy=1")
        except:
            print(r)
        soup = BeautifulSoup(r.text, "lxml")
        data = soup.find_all("div",{"class":"result location-data-result show-on-map"})
        length1 = len(data)
        # print(length1)
        for i in data:
            location_name = i.find("span",{"class":"dataFacilityName hidden"}).text.strip()
            street_address = i.find("span",{"class":"dataAddress1 hidden"}).text.strip()
            if "2924 W Van Buren Street" in street_address:
                continue
            city = i.find("span",{"class":"dataCity hidden"}).text.strip()
            state = i.find("span",{"class":"dataState hidden"}).text.strip()
            if "LC" in state or "TC" in state:
                continue
            zipp = i.find("span",{"class":"dataZip hidden"}).text.strip()
            if len(zipp) == 5:
                zipp = zipp
            else:
                zipp = str(zipp[:5])+"-"+str(zipp[5:])
            phone = i.find("span",{"class":"dataPhoneNumber hidden"}).text.strip()
            latitude = i.find("span",{"class":"lat hidden"}).text.strip()
            longitude = i.find("span",{"class":"long hidden"}).text.strip()
            hours_of_operation = "Monday - Friday:"+" "+str(i.find("span",{"class":"dataMFHours hidden"}).text.strip())\
                +" "+"Saturday:"+" "+str(i.find("span",{"class":"dataSatHours hidden"}).text.strip())\
                    +" "+"Sunday:"+" "+str(i.find("span",{"class":"dataSunHours hidden"}).text.strip())
            location_type = "Mechanical Center"
            if "=" in i.find("a",{"class":"btnStoreSite"})['href']:
                page_url = "https://www.napaautocare.com"+i.find("a",{"class":"btnStoreSite"})['href'].replace("http://locator.carolinas.aaa.com/nc/charlotte/5844/carcare?q=28210&loc=28210%2c+nc&t=","/store.aspx?id=595060")
                store_number = i.find("a",{"class":"btnStoreSite"})['href'].split("=")[1].replace("28210&loc","595060")
            else:
                for num in i.find_all(lambda tag: (tag.name == "span") and "Dealer Location" in tag.text):
                    store_number = (num.text.split(" ")[-1])
                    page_url = "https://www.napaautocare.com/store.aspx?id="+str(store_number)

            result_coords.append((latitude,longitude))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp.replace("00000","<MISSING>"))
            store.append("US")
            store.append(store_number)
            store.append(phone )
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            #print("data ====="+str(store))
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            yield store

        r1 = requests.get("https://www.napaautocare.com/store-finder.aspx?zip="+str(zip_code)+"&address=undefined&city=&state=&storetype=Collision%20Center&distance="+str(MAX_DISTANCE)+"&filter=undefined&autocareFilter=false&aaaAutoApproved=false&cbCharge=false&sortBy=1")
        soup1 = BeautifulSoup(r1.text, "lxml")
        data1 = soup1.find_all("div",{"class":"result location-data-result show-on-map"})
        length2 = len(data1)
        # print(length2)
        for j in data1:
            location_name1 = j.find("span",{"class":"dataFacilityName hidden"}).text.strip()
            street_address1 = j.find("span",{"class":"dataAddress1 hidden"}).text.strip()
            city1 = j.find("span",{"class":"dataCity hidden"}).text.strip()
            state1 = j.find("span",{"class":"dataState hidden"}).text.strip()
            zipp1 = j.find("span",{"class":"dataZip hidden"}).text.strip()
            if len(zipp1) == 5:
                zipp1 = zipp1
            else:
                zipp1 = str(zipp1[:5])+"-"+str(zipp1[5:])
            phone1 = j.find("span",{"class":"dataPhoneNumber hidden"}).text.strip()
            latitude1 = j.find("span",{"class":"lat hidden"}).text.strip()
            longitude1 = j.find("span",{"class":"long hidden"}).text.strip()
            hours_of_operation1 = "Monday - Friday:"+" "+str(j.find("span",{"class":"dataMFHours hidden"}).text.strip())\
                +" "+"Saturday:"+" "+str(j.find("span",{"class":"dataSatHours hidden"}).text.strip())\
                    +" "+"Sunday:"+" "+str(j.find("span",{"class":"dataSunHours hidden"}).text.strip())
            location_type1 = "Collision Center"
            if "=" in j.find("a",{"class":"btnStoreSite"})['href']:
                page_url1 = "https://www.napaautocare.com"+j.find("a",{"class":"btnStoreSite"})['href']
                store_number1 = j.find("a",{"class":"btnStoreSite"})['href'].split("=")[1]
            else:
                for num1 in j.find_all(lambda tag: (tag.name == "span") and "Dealer Location" in tag.text):
                    store_number1 = (num1.text.split(" ")[-1])
                    page_url1 = "https://www.napaautocare.com/store.aspx?id="+str(store_number1)
            


            result_coords.append((latitude,longitude))
            store1 = []
            store1.append(base_url)
            store1.append(location_name1)
            store1.append(street_address1)
            store1.append(city1)
            store1.append(state1)
            store1.append(zipp1)
            store1.append("US")
            store1.append(store_number1)
            store1.append(phone1)
            store1.append(location_type1)
            store1.append(latitude1)
            store1.append(longitude1)
            store1.append(hours_of_operation1)
            store1.append(page_url1)
            if store1[2] in addresses1:
                continue
            addresses1.append(store1[2])
            #print("data ====="+str(store))
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            yield store1
        

        r2 = requests.get("https://www.napaautocare.com/store-finder.aspx?zip="+str(zip_code)+"&address=undefined&city=&state=&storetype=Truck%20Center&distance="+str(MAX_DISTANCE)+"&filter=undefined&autocareFilter=false&aaaAutoApproved=false&cbCharge=false&sortBy=1")
        soup2 = BeautifulSoup(r2.text, "lxml")
        data2 = soup2.find_all("div",{"class":"result location-data-result show-on-map"})
        length3 = len(data2)
        # print(length3)
        for k in data2:
            location_name2 = k.find("span",{"class":"dataFacilityName hidden"}).text.strip()
            street_address2 = k.find("span",{"class":"dataAddress1 hidden"}).text.strip()
            city2 = k.find("span",{"class":"dataCity hidden"}).text.strip()
            state2 = k.find("span",{"class":"dataState hidden"}).text.strip()
            if "BS" in state2:
                continue

            zipp2 = k.find("span",{"class":"dataZip hidden"}).text.strip()
            if len(zipp2) == 5:
                zipp2 = zipp2
            else:
                zipp2 = str(zipp2[:5])+"-"+str(zipp2[5:])
            phone2 = k.find("span",{"class":"dataPhoneNumber hidden"}).text.strip()
            latitude2 = k.find("span",{"class":"lat hidden"}).text.strip()
            longitude2 = k.find("span",{"class":"long hidden"}).text.strip()
            hours_of_operation2 = "Monday - Friday:"+" "+str(k.find("span",{"class":"dataMFHours hidden"}).text.strip())\
                +" "+"Saturday:"+" "+str(k.find("span",{"class":"dataSatHours hidden"}).text.strip())\
                    +" "+"Sunday:"+" "+str(k.find("span",{"class":"dataSunHours hidden"}).text.strip())
            location_type2 = "Truck Center"

            if "=" in k.find("a",{"class":"btnStoreSite"})['href']:
                page_url2 = "https://www.napaautocare.com"+k.find("a",{"class":"btnStoreSite"})['href']
                store_number2 = k.find("a",{"class":"btnStoreSite"})['href'].split("=")[1]
            else:
                for num2 in k.find_all(lambda tag: (tag.name == "span") and "Dealer Location" in tag.text):
                    store_number2 = (num2.text.split(" ")[-1])
                    page_url2 = "https://www.napaautocare.com/store.aspx?id="+str(store_number2)


            result_coords.append((latitude,longitude))
            store2 = []
            store2.append(base_url)
            store2.append(location_name2)
            store2.append(street_address2)
            store2.append(city2)
            store2.append(state2.replace("-1","<MISSING>"))
            store2.append(zipp2.replace("00000","<MISSING>"))
            store2.append("US")
            store2.append(store_number2)
            store2.append(phone2)
            store2.append(location_type2)
            store2.append(latitude2)
            store2.append(longitude2)
            store2.append(hours_of_operation2)
            store2.append(page_url2)
            if store2[2] in addresses2:
                continue
            addresses2.append(store2[2])
            #print("data ====="+str(store))
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            yield store2


        current_results_len = length1+length2+length3 
        # print(current_results_len)
        if current_results_len < MAX_RESULTS:
                # print("max distance update")
                search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)

scrape()

