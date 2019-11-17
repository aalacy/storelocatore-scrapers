import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    store_detail = []
    store_name = []
    return_main_object = []
    address1 = []
    longitude =''
    country_code = 'US'
    location_type = ''
    store_number =''
    latitude = ''
    base_url = 'http://vercenterprises.com/locations.htm'
    locator_domain = 'http://vercenterprises.com'
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")   
    p_tage= soup.find_all('p', {'class': 'bodyTextL'})[0]
    p_tage1= soup.find_all('p', {'class': 'bodyTextL'})[1]
    p_tage2 = soup.find_all('p', {'class': 'bodyTextL'})[2:]
    # print(soup.find_all('p', {'class': 'bodyTextL'})[2:])
    # arr2 = (str(p_tage1).split("</a>"))
    for i in range(len(p_tage2)):
        new = p_tage2[i].find("a",{"href":re.compile("http://maps")}) 
        
        
        latitude = str(new).split("ll=")[-1].split(",")[0]
        longitude = str(new).split("ll=")[-1].split(",")[1].split("&")[0]
        
        location_name = p_tage2[i].find("b").text.replace("\n","")
        arr2 = str(p_tage2[i]).split("</a>")[0]
        soup2 = BeautifulSoup(p_tage2[i].text, "lxml")
        # print(str(p_tage2[i]).split('width="107"/></a>'))
   
        

        #
        phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(soup2.text.replace(location_name,"")))[-1]
        zip1 = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(soup2.text.replace(location_name,"")))[-1]
        state = re.findall(r' ([A-Z]{2})', str(soup2.text.replace(location_name,"")))[-1]
        address_list1 =soup2.text.split("\n")
      
        

        index = [i for i, s in enumerate(address_list1) if 'Shift' in s]
        index1 = [i for i, s in enumerate(address_list1) if 'Team' in s]
        if index != []:
            addressess = address_list1[index[0]+1:][0]
            city = address_list1[index[0]+1:][1].split(",")[0]
            hours_of_operation =(" ".join(address_list1[index[0]+1:][-3:]).replace(phone,"").replace("( ","").split(zip1)[-1].split("Location")[0].strip())
        elif index1 != []:
            kv = address_list1[index1[0]+1:]
            if address_list1[index1[0]+1:][0]=="Food Service Leader: Rich Holmgren":
                del kv[0]
            addressess = kv[0]
            city = (kv[1].split(',')[0])
            hours_of_operation =(" ".join(kv[2:]).replace(phone,"").replace("(","").split("Location")[0])
        else:
            addressess = address_list1[1:][0]
            city = (address_list1[1:][1].split(",")[0])
            hours_of_operation = (" ".join(address_list1[1:][2:]).replace(phone,"").replace("(",""))


        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(addressess if addressess else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip1 if zip1 else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation.replace("www.britewaycarwash.com","").strip() if hours_of_operation.replace("www.britewaycarwash.com","") else '<MISSING>')
        store.append("<MISSING>")
        yield store

    arr1 = (str(p_tage1).split("</a>"))
    for i in  range(len(arr1))[:-1]:
        soup2 = BeautifulSoup(arr1[i], "lxml")
        location_name = soup2.find("b").text.replace("\n","")
        phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(soup2.text.replace(location_name,"")))[-1]
        zip1 = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(soup2.text.replace(location_name,"")))[-1]
        state = re.findall(r' ([A-Z]{2})', str(soup2.text.replace(location_name,"")))[-1]
        address_list1 =list(soup2.stripped_strings)
        
        lat = (soup2.find("a")['href'].split("/@"))
        lat1 = soup2.find("a")['href'].split("ll=")
        
        if len(lat)==2:
            latitude =lat[-1].split(",")[0]
            longitude = lat[-1].split(",")[1]
        else:
            if len(lat[0].split("ll="))==1:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            else:
                latitude = lat[0].split("ll=")[-1].split(",")[0]
                longitude = lat[0].split("ll=")[-1].split(",")[1].split("&")[0]


        index = [i for i, s in enumerate(address_list1) if 'Shift' in s]
        index1 = [i for i, s in enumerate(address_list1) if 'Team' in s]
        if index != []:
            addressess = address_list1[index[0]+1:][0]
            city = address_list1[index[0]+1:][1].split(",")[0]
            hours_of_operation =(" ".join(address_list1[index[0]+1:][-3:]).replace(phone,"").replace("( ","").split(zip1)[-1].split("Location")[0].strip())
        elif index1 != []:
            kv = address_list1[index1[0]+1:]
            if address_list1[index1[0]+1:][0]=="Food Service Leader: Rich Holmgren":
                del kv[0]
            addressess = kv[0]
            city = (kv[1].split(',')[0])
            hours_of_operation =(" ".join(kv[2:]).replace(phone,"").replace("(","").split("Location")[0])
        else:
            addressess = address_list1[1:][0]
            city = (address_list1[1:][1].split(",")[0])
            hours_of_operation = (" ".join(address_list1[1:][2:]).replace(phone,"").replace("(",""))
        
        # print(addressess)
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(addressess if addressess else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip1 if zip1 else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation.strip() if hours_of_operation else '<MISSING>')
        store.append("<MISSING>")
        yield store

    arr =str(p_tage).split("></a>")
   

    for i in range(len(arr))[:-1]:
        store =[]
        soup1 = BeautifulSoup(arr[i], "lxml")
        location_name = soup1.find("b").text.replace("\n","")
        phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(soup1.text.replace(location_name,"")))[-1]
        zip1 = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(soup1.text.replace(location_name,"")))[-1]
        state = re.findall(r' ([A-Z]{2})', str(soup1.text.replace(location_name,"")))[-1]
        address_list =list(soup1.stripped_strings)
        lat = (soup1.find("a")['href'].split("/@"))
        lat1 = soup1.find("a")['href'].split("ll=")
        
        if len(lat)==2:
            latitude =lat[-1].split(",")[0]
            longitude = lat[-1].split(",")[1]
        else:
            if len(lat[0].split("ll="))==1:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            else:
                latitude = lat[0].split("ll=")[-1].split(",")[0]
                longitude = lat[0].split("ll=")[-1].split(",")[1].split("&")[0]
        
        age_index = [i for i, s in enumerate(address_list) if 'Shift' in s]
        age_index1 = [i for i, s in enumerate(address_list) if 'Team' in s]
        if age_index != []:
            addressess = address_list[age_index[0]+1:][0]
            city = address_list[age_index[0]+1:][1].split(",")[0]
            hours_of_operation =(" ".join(address_list[age_index[0]+1:][-3:]).replace(phone,"").replace("( ","").split(zip1)[-1].split("Location")[0].strip())
        elif age_index1 != []:
            kv = address_list[age_index1[0]+1:]
            if address_list[age_index1[0]+1:][0]=="Food Service Leader: Rich Holmgren":
                del kv[0]
            addressess = kv[0]
            city = (kv[1].split(',')[0])
            hours_of_operation =(" ".join(kv[2:]).replace(phone,"").replace("(","").split("Location")[0])
        else:
            addressess = address_list[1:][0]
            city = (address_list[1:][1].split(",")[0])
            hours_of_operation = (" ".join(address_list[1:][2:]).replace(phone,"").replace("(",""))

           
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(addressess if addressess else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip1 if zip1 else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation.strip() if hours_of_operation else '<MISSING>')
        store.append("<MISSING>")
        yield store
        # print(store)

       
         


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
