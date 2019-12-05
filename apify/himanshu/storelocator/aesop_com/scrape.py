import csv
import sys
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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Authorization":"Bearer d168a942b4814ef725c58d116dd157544b1101864315194cf3cc1c51735ad459",
    }
    base_url = "https://www.aesop.com"

    addresses123 = []
    op =[]
    addresses=[]
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    # current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()    # zip_code = search.next_zip()    
    
    while coord:
        result_coords = []
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        zipcode = ''
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        lat = coord[0]
        lng = coord[1]
        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        #print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        # lat = -42.225
        # lng = -42.225
        # zip_code = 11576
        location_url = "https://cdn.contentful.com/spaces/q8kkhxjupn16/entries?locale=en&content_type=storeDetail&include=2&fields.location%5Bwithin%5D="+ str(lat) + "%2C"+ str(lng)
        # print('location_url ==' +location_url))
        try:
            r = requests.get(location_url, headers=headers)
        except:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        k = json.loads(soup.text)['items']
        current_results_len = len(k)  
        for i in k:
            city =''
            if "country" in i['fields']:
                country_code =  i['fields']["country"]
                if country_code.strip().lstrip()=="US" or country_code.strip().lstrip()=="CA":
                    # print("==============================")
                    v = i['fields']['formattedAddress']
                    name1 = i['fields']['storeName']
                    lat = i['fields']['location']['lat']
                    lng = i['fields']['location']['lon']
                    if "phone" in i['fields']:
                        phone = i['fields']['phone'].replace("=","+")

                    # print(i['fields']['phone'])
                    # if "state" in i['fields']:
                    #     state = i['fields']python['state']
            
                    
                    # if "city" in i['fields']:
                    #     city = i['fields']['city']
        

                    ln = len(v.replace(", Canada","").replace(", USA","").split(","))
                    if ln==3:
                        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(v.replace(", Canada","").replace(", USA","").split(",")))
                        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(v.replace(", Canada","").replace(", USA","").split(",")[1:]))
                        state_list = re.findall(r' ([A-Z]{2}) ', str(v.replace(", Canada","").replace(", USA","").split(",")[1:]))
                        if us_zip_list:
                            zipp = us_zip_list[-1]

                        if ca_zip_list:
                            zipp = ca_zip_list[-1]

                        if state_list:
                            state = state_list[-1]
                        st = v.replace(", Canada","").replace(", USA","").split(",")[0]
                        city = v.replace(", Canada","").replace(", USA","").split(",")[1].replace("1101D","").replace("NY","").replace("Viateur Ouest","")
                        # print(v.replace(", Canada","").replace(", USA","").split(",")[1].replace("1101D","").replace("NY","").replace("Viateur Ouest",""))
                    
                    elif ln==4:
                        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(v.replace(", Canada","").replace(", USA","").split(",")[1:])))
                        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(" ".join(v.replace(", Canada","").replace(", USA","").split(",")[1:])))
                        state_list = re.findall(r' ([A-Z]{2}) ', str(" ".join(v.replace(", Canada","").replace(", USA","").split(",")[2:])))
                        if us_zip_list:
                            zipp = us_zip_list[-1]

                        if ca_zip_list:
                            zipp = ca_zip_list[-1]
        
                        city = v.replace(", Canada","").replace(", USA","").split(",")[1].replace(" Suite 2245","")
                        st = (" ".join(v.replace(", Canada","").replace(", USA","").split(",")[:2]).replace(city,""))
                    elif ln==5:
                        zipp = v.replace(", Canada","").replace(", USA","").split(",")[-1].strip()
                        state = v.replace(", Canada","").replace(", USA","").split(",")[-2].strip()
                        city = v.replace(", Canada","").replace(", USA","").split(",")[-3].strip()
                        st = " ".join(v.replace(", Canada","").replace(", USA","").split(",")[:2])
                
                    if ln ==2:
                        st = v.replace(", Canada","").replace(", USA","").split(",")[0].split(".")[0]
                        city = v.replace(", Canada","").replace(", USA","").split(",")[0].split(".")[1]
                        state = v.replace(", Canada","").replace(", USA","").split(",")[-1].strip().split(" ")[0]
                        zipp = v.replace(", Canada","").replace(", USA","").split(",")[-1].strip().split(" ")[1]

                    tem_var =[]
                    tem_var.append("https://www.aesop.com")
                    tem_var.append(name1 if name1 else "<MISSING>" )
                    tem_var.append(st if st else "<MISSING>"  )
                    tem_var.append(city if city else "<MISSING>" )
                    tem_var.append(state if state else "<MISSING>" )
                    tem_var.append(zipp if zipp else "<MISSING>" )
                    tem_var.append(country_code)
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("<MISSING>")
                    tem_var.append(lat if lat else "<MISSING>" )
                    tem_var.append(lng if lng else "<MISSING>" ) 
                    tem_var.append("<MISSING>" )
                    tem_var.append("<MISSING>" )
                    if tem_var[2] in addresses:
                        continue
                    addresses.append(tem_var[2])
                    yield tem_var
                    #print("----------------------------------",tem_var)
                   
                        # print(v.replace(", Canada","").replace(", USA","").split(",")[-1].strip().split(" ")[1])    # print(v.replace(", Canada","").replace(", USA","").split(","))
                    # print(v.replace(", Canada","").replace(", USA","").split(",")[-1])

                    # print(v.replace(", Canada","").replace(", USA","").split(",")[1:])
                    

                    # lat = i['fields']['location']['lat']
                    # lng  =  i['fields']['location']['lon']
                    # if  "phone" in i['fields']:
                    #     phone = i['fields']['phone']
                    # if "state" in i['fields']:
                    #     state = i['fields']['state']
                    # # print(state)
                    # location_name = i['fields']['storeName']
                    # location_type = i['fields']["storeType"]

                    # if "city" in i['fields']:
                    #     city = i['fields']["city"]

                    # if "country" in i['fields']:
                    #     country_code =  i['fields']["country"]
                    #     print(country_code)
            
                    
                    # street_address1  = v.replace(state ,"").replace(city ,"")
                    # us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(v))
                    # ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str())
                    
                    # if us_zip_list:
                    #     street_address  = street_address1.replace(us_zip_list[-1],"").replace(", , ,"," ").replace(",  ,"," ")
                    # else:
                    #     street_address = street_address1
                    


                    # if us_zip_list:
                    #     street_address  = street_address1.replace(us_zip_list[-1],"").replace(", , ,"," ").replace(",  ,"," ")
                    # else:
                    #     street_address = street_address1
                    # if us_zip_list:
                    #     zipp = us_zip_list[-1]

                    # page_url = "https://www.aesop.com/us/?visitMenu=open"
                    # latitude = lat
                    # longitude = lng
                    # raw_address = street_address
                    # result_coords.append((latitude, longitude))
                    # store = [locator_domain, location_name, "<INACCESSIBLE>", city.encode('ascii', 'ignore').decode('ascii').strip(), state.encode('ascii', 'ignore').decode('ascii').strip(), zipp, country_code,
                    #         store_number, phone, location_type, latitude, longitude, hours_of_operation,raw_address.encode('ascii', 'ignore').decode('ascii').strip().replace(", , ,"," ").replace(",  ,"," "),page_url]

            
                    # if store[-2] in addresses123:
                    #     continue
                    # addresses123.append(store[-2])
            
                    # store = [x if x else "<MISSING>" for x in store]
                    # # print("data = " + str(store))
                    # # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    # yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()   # zip_code = search.next_zip()    
        # break

def scrape():
    data = fetch_data()

    write_output(data)


scrape()
