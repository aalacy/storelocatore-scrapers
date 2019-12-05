import csv
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


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        return str(hour) + ":00" + " " + am
    else:
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
    
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 80
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    
    return_main_object = []
    addresses = []
  

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "content-type": "application/json;charset=UTF-8",
  
        
    }

    # it will used in store data.
    locator_domain = "https://www.drmartens.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "drmartens"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    address=[]
    while coord:
        result_coords = []
        try:
            r = requests.get(
                "https://www.kwiktrip.com/locproxy.php?Latitude="+str(coord[0])+"&Longitude="+str(coord[1])+"&maxDistance="+str(MAX_DISTANCE)+"&limit="+str(MAX_RESULTS),
                headers=headers,
        
            )
            soup= BeautifulSoup(r.text,"lxml")
            k = json.loads(soup.text)
        except:
            continue
    # print("=====================================================================",soup)
    # print('https://www.kwiktrip.com/locproxy.php?Latitude='+zip_code[0]+'&Longitude='+zip_code[1] +'&maxDistance='+str(MAX_DISTANCE)+'&limit='+str(MAX_RESULTS))
        
        if len(k) != 1 or k in 'stores':
            current_results_len = len(k['stores'])
            for i in k['stores']:
                # print("=====================================================================",i)
                tem_var=[]
                if i['open24Hours']==True:
                    hours_of_operation = "Open 24 hours a day"
                else:
                    hours_of_operation ="<MISSING>"
                tem_var.append("https://www.kwiktrip.com")
                tem_var.append(i['name'].split(" #")[0])
                tem_var.append(i['address']['address1'])
                tem_var.append(i['address']['city'] )
                tem_var.append(i['address']['state'])
                tem_var.append(i['address']['zip'])
                tem_var.append("US")
                tem_var.append(i['name'].split(" #")[-1])
                tem_var.append(i['phone'])
                tem_var.append("<MISSING>")
                tem_var.append(i['latitude'])
                tem_var.append(i['longitude'])
                tem_var.append(hours_of_operation)
                tem_var.append('<MISSING>')
                if tem_var[2] in address:
                    continue

                address.append(tem_var[2])
                # print("tem_var==============================",tem_var)
                yield tem_var
            # return_main_object.append(tem_var)
            
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
       
    # return return_main_object


            

def scrape():
    data = fetch_data()
    write_output(data)


scrape()



