import csv
import sys
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lincoln_com')
session = SgRequests()

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
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://www.lincoln.com/dealerships/",
        "x-dtpc": "6$105614484_619h2vUDAFDUIIQFURTHRADJWNKGVAPCPTIVHV-0e3",
        "X-Requested-With": "XMLHttpRequest"

    }
    base_url = "https://www.lincoln.com"
    addresses1 = []
    addresses = []
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

        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        # lat = -42.225
        # lng = -42.225

        # zip_code = 11576
        get_u = "https://www.lincoln.com/services/dealer/Dealers.json?make=Lincoln&radius="+str(MAX_DISTANCE)+"&filter=&minDealers=1&maxDealers="+str(MAX_RESULTS)+"&postalCode="+str(zip_code)+"&api_key=0d571406-82e4-2b65-cc885011-048eb263"
        # location_url = "https://www.lincoln.com/services/dealer/Dealers.json?make=Lincoln&radius="+str(MAX_DISTANCE)+"&filter=&minDealers=1&maxDealers="+str(MAX_RESULTS)+"&postalCode="+str(zip_code)
        # logger.info('location_url ==' +location_url))
        try:
            k = session.get(get_u, headers=headers).json()
        except:
            continue
        if "Response" in k and "Dealer" in k['Response']:
            if list ==type(k['Response']["Dealer"]):
                x = len(k['Response']["Dealer"])
                for i in k['Response']['Dealer']:
                    if i['ldlrcalltrk_lad']:
                        phone =  i['ldlrcalltrk_lad']
                    else:
                        phone = i["Phone"]
                    if "Street1"  in i["Address"]:
                        street_address = i["Address"]['Street1'] #+ ' ' +i["Address"]['Street2']+ ' ' +i["Address"]['Street3']
                    else:
                        street_address = "<MISSING>"
                    city = i["Address"]['City']
                    state = i["Address"]['State']
                    zipp =i["Address"]['PostalCode']
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
                    tem_var1 =[]
                    store_name.append(i["Name"])
                    tem_var1.append(street_address)
                    tem_var1.append(city)
                    tem_var1.append(state)
                    tem_var1.append(zipp)
                    tem_var1.append("US")
                    tem_var1.append("<MISSING>")
                    tem_var1.append(phone if phone else "<MISSING>" )
                    tem_var1.append("<MISSING>")
                    tem_var1.append(latitude)
                    tem_var1.append(longitude)
                    tem_var1.append(hours_of_operation.replace(" SalesHours  ServiceHours ","<MISSING>") if hours_of_operation else "<MISSING>")
                    tem_var1.append("https://www.lincoln.com/dealerships/dealer-details/"+i['urlKey'])
                    store_detail.append(tem_var1)
                    # logger.info(tem_var1)
          

        if "Response" in k and "Dealer" in k['Response']:
            if dict==type(k['Response']["Dealer"]):
                y = len(k['Response']["Dealer"])
                
                if "Street1"  in k['Response']["Dealer"]["Address"]:
                    street_address = k['Response']["Dealer"]["Address"]['Street1'] 
                else:
                    street_address = "<MISSING>"

                # logger.info(street_address)

                if k['Response']["Dealer"]['ldlrcalltrk_lad']:
                    phone =  k['Response']["Dealer"]['ldlrcalltrk_lad']
                else:
                    phone = k['Response']["Dealer"]["Phone"]

                
                city = k['Response']["Dealer"]["Address"]['City']
                state = k['Response']["Dealer"]["Address"]['State']
                zipp =k['Response']["Dealer"]["Address"]['PostalCode']
                # phone = i["Phone"]
                time=''
                time1 = ''
                h1 =''
                if "Day" in k['Response']["Dealer"]["SalesHours"]:
                    for j in k['Response']["Dealer"]["SalesHours"]['Day']:
                        if "closed" in j and j=="true":
                            h1  = j['name'] + ' ' +"closed"
                        elif "open" in j:
                            time =  time + ' '+j['name'] + ' ' +j['open'] + ' '+j['close'] + ' '+h1
            
                if "Day" in k['Response']["Dealer"]["ServiceHours"]:
                    for j in k['Response']["Dealer"]["ServiceHours"]['Day']:
                        if "closed" in j and j=="true":
                            h1  = j['name'] + ' ' +"closed"
                        elif "open" in j:
                            time1 = time1 + ' '+j['name'] + ' ' +j['open'] + ' '+j['close'] + ' '+h1

                hours_of_operation = " SalesHours " + time + " ServiceHours " + time1
                latitude = k['Response']["Dealer"]['Latitude']
                longitude = k['Response']["Dealer"]['Longitude']
                tem_var =[]
                # tem_var.append("https://www.lincoln.com")
                store_name.append(k['Response']["Dealer"]["Name"])
                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipp)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone if phone else "<MISSING>" )
                tem_var.append("<MISSING>")
                tem_var.append(latitude)
                tem_var.append(longitude)
                tem_var.append(hours_of_operation.replace(" SalesHours  ServiceHours ","<MISSING>") if hours_of_operation else "<MISSING>")
                tem_var.append("https://www.lincoln.com/dealerships/dealer-details/"+i['urlKey'])
                store_detail.append(tem_var)            
                # logger.info(tem_var)
     
        result_coords.append((latitude, longitude))
        if x+y < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif x+y == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        # coord = search.next_coord()   # zip_code = search.next_zip()  
        zip_code = search.next_zip()  
    
    # logger.info(len(store_name))
    # logger.info(len(store_detail))

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
