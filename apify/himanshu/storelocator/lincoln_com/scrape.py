import csv
import sys

import requests
from bs4 import BeautifulSoup
import re
import json
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
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
    }
    base_url = "https://www.lincoln.com"

    addresses = []
    addresses1 =[]
    store_detail =[] 
    store_name=  []
    return_man = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    y =0
    x =0
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    # coord = search.next_coord()    # zip_code = search.next_zip() 
    zip_code = search.next_zip()       
    
    while zip_code:
        result_coords = []

        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = "lincoln"
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""


        # lat = coord[0]
        # lng = coord[1]

        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        # lat = -42.225
        # lng = -42.225

        # zip_code = 11576
        location_url = "https://www.lincoln.com/services/dealer/Dealers.json?make=Lincoln&radius="+str(MAX_DISTANCE)+"&filter=&minDealers=1&maxDealers="+str(MAX_RESULTS)+"&postalCode="+str(zip_code)
        # print('location_url ==' +location_url))
        try:
            k = requests.get(location_url, headers=headers).json()
        except:
            continue
        if "Response" in k and "Dealer" in k['Response']:
            if list ==type(k['Response']["Dealer"]):
                x = len(k['Response']["Dealer"])
                for i in k['Response']['Dealer']:
                    
                    if "Street1"  in i["Address"]:
                        street_address = i["Address"]['Street1'] #+ ' ' +i["Address"]['Street2']+ ' ' +i["Address"]['Street3']
                    else:
                        street_address = "<MISSING>"
                    # location_name = i["Name"]
                    store_name.append(i["Name"])
                    city = i["Address"]['City']
                    state = i["Address"]['State']
                    zipp =i["Address"]['PostalCode']
                    phone = i["Phone"]
                    time=''
                    time1 = ''
                    h1 =''
                    if  "Day" in i["SalesHours"]:
                        for j in i["SalesHours"]['Day']:
                            if "closed" in j and j=="true":
                                h1  = j['name'] + ' ' +"closed"
                            elif "open" in j:
                                time =  time + ' '+j['name'] + ' ' +j['open'] + ' '+j['close'] + ' '+h1
                
                    if  "Day" in i["ServiceHours"]:
                        for j in i["ServiceHours"]['Day']:
                            if "closed" in j and j=="true":
                                h1  = j['name'] + ' ' +"closed"
                            elif "open" in j:
                                time1 = time1 + ' '+j['name'] + ' ' +j['open'] + ' '+j['close'] + ' '+h1
                    hours_of_operation = " SalesHours " + time + " ServiceHours " + time1
                    latitude = i['Latitude']
                    longitude = i['Longitude']
                    tem_var =[]
                    tem_var.append(street_address)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zipp)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone if phone else "<MISSING>" )
                    tem_var.append("lincoln")
                    tem_var.append(latitude)
                    tem_var.append(longitude)
                    tem_var.append(hours_of_operation.replace(" SalesHours  ServiceHours ","<MISSING>") if hours_of_operation else "<MISSING>")
                    tem_var.append("https://www.lincoln.com/dealerships/dealer-details/"+i['urlKey'])
                    
                    store_detail.append(tem_var)
          

        if "Response" in k and "Dealer" in k['Response']:
            if dict==type(k['Response']["Dealer"]):
                y = len(k['Response']["Dealer"])
                if "Street1"  in i["Address"]:
                    street_address = i["Address"]['Street1'] #+ ' ' +i["Address"]['Street2']+ ' ' +i["Address"]['Street3']
                else:
                    street_address = "<MISSING>"
                store_name.append(i["Name"])
                city = i["Address"]['City']
                state = i["Address"]['State']
                zipp =i["Address"]['PostalCode']
                phone = i["Phone"]
                time=''
                time1 = ''
                h1 =''
                if "Day" in i["SalesHours"]:
                    for j in i["SalesHours"]['Day']:
                        if "closed" in j and j=="true":
                            h1  = j['name'] + ' ' +"closed"
                        elif "open" in j:
                            time =  time + ' '+j['name'] + ' ' +j['open'] + ' '+j['close'] + ' '+h1
            
                if "Day" in i["ServiceHours"]:
                    for j in i["ServiceHours"]['Day']:
                        if "closed" in j and j=="true":
                            h1  = j['name'] + ' ' +"closed"
                        elif "open" in j:
                            time1 = time1 + ' '+j['name'] + ' ' +j['open'] + ' '+j['close'] + ' '+h1

                hours_of_operation = " SalesHours " + time + " ServiceHours " + time1
                latitude = i['Latitude']
                longitude = i['Longitude']
                tem_var =[]
                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipp)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone if phone else "<MISSING>" )
                tem_var.append("lincoln")
                tem_var.append(latitude)
                tem_var.append(longitude)
                tem_var.append(hours_of_operation.replace(" SalesHours  ServiceHours ","<MISSING>") if hours_of_operation else "<MISSING>")
                tem_var.append("https://www.lincoln.com/dealerships/dealer-details/"+i['urlKey'])
                store_detail.append(tem_var)
     

        if x+y < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif x+y == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        # coord = search.next_coord()   # zip_code = search.next_zip()  
        zip_code = search.next_zip()  


    for i in range(len(store_name)):
        store = list()
        store.append("https://www.lincoln.com")
        store.append(store_name[i])                 
        store.extend(store_detail[i])
        if store[2] in addresses:
            continue
        addresses.append(store[2])  
        return_man.append(store)  
    return return_man
        # break

def scrape():
    data = fetch_data()

    write_output(data)


scrape()
