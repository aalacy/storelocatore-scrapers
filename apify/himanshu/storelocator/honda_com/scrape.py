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
    # zips = sgzip.coords_for_radius(50)

    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 100
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()  

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "content-type": "application/json;charset=UTF-8",
        'X-Requested-With':"XMLHttpRequest"    
    }

    # it will used in store data.
    
    address=[]
    
    while zip_code:
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
        st =  "<MISSING>"

        result_coords = []
        #print(zip_code)
        r = requests.get(
            'https://owners.honda.com/service-maintenance/dealer-search?zip='+str(zip_code)+'&searchRadius='+str(MAX_DISTANCE),
            headers=headers,
       
        )
        name =''
        soup= BeautifulSoup(r.text,"lxml")
        try:
            k = json.loads(soup.text)
        except:
            continue
        time =''
        if k != None and k !=[]:
            current_results_len = len(k['Dealers'])
            for i in k['Dealers']:
                h1= (i['Departments'])

                p=''
                for h in h1:
                    t=''
                    type1 = h['Type']
                    for q in h['OperationHours']:
                        t= t+' '+q['Day']+ ' '+q['Hours']
                    time = time +' ' +type1 + ' '+t

                #print(i)
                # print(p)
                # exit()
                
                if "Name" in i:
                    name  = i['Name']
                
                if "Address" in i:
                    st = i['Address']['AddressLine1']
                    state = i['Address']['State']
                    city = i['Address']['City'].strip()
                    zipp = i['Address']['Zip']
                    latitude = str(i['Address']['Latitude'])
                    longitude = str(i['Address']['Longitude'])

                if "Phone" in i:
                    phone = i['Phone']

                # result_coords.append((latitude, longitude))
                tem_var =[]
                tem_var.append("https://www.honda.com/")
                tem_var.append(name if name else "<MISSING>" )
                tem_var.append(st)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipp)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("<MISSING>")
                tem_var.append(latitude)
                tem_var.append(longitude)
                tem_var.append(time if time else "<MISSING>" )
                tem_var.append("<MISSING>")
                
                if tem_var[2] in addresses:
                    continue
                addresses.append(tem_var[2])
                yield tem_var
                # print("============================")
                # print(tem_var)
                # exit()

        if current_results_len < MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
    # return return_main_object


            

def scrape():
    data = fetch_data()
    write_output(data)


scrape()



