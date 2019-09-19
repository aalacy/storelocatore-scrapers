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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    zips = sgzip.for_radius(100)
    # zips = sgzip.coords_for_radius(50)

    
    return_main_object = []
    addresses = []
    store_name=[]
    store_detail=[]
  

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "content-type": "application/json;charset=UTF-8",
  
        
    }

    # it will used in store data.
    # locator_domain = "https://www.drmartens.com"
    # location_name = ""
    # street_address = "<MISSING>"
    # city = "<MISSING>"
    # state = "<MISSING>"
    # zipp = "<MISSING>"
    # country_code = "US"
    # store_number = "<MISSING>"
    # phone = "<MISSING>"
    # location_type = "drmartens"
    # latitude = "<MISSING>"
    # longitude = "<MISSING>"
    # raw_address = ""
    # hours_of_operation = "<MISSING>"
    address=[]
    for zip_code in zips:
        try:
            r = requests.get(
                'https://redsky.target.com/v3/stores/nearby/'+ zip_code +'?key=eb2551e4accc14f38cc42d32fbc2b2ea&limit=20&within=100&unit=mile',
                headers=headers,
        
            )
            soup= BeautifulSoup(r.text,"lxml")
            k = json.loads(soup.text)
        
            
            # if k !=[]:
            time =''
            if k != None and k !=[]:
                for i in k:
                    
                    for j in i['locations']:
                        tem_var=[]
                    #     print(j['address']['city'])
                    # exit()
                        # if 'hours' in i and i['hours'] !=None:
                        #     for j in i['hours']:
                        #         time = time +' ' +(j['day']+ ' '+j['formattedTime'])
                        # else:
                        #     time = ''
                        h1 = j['rolling_operating_hours']['regular_event_hours']['days']
                        time =''
                        for h in h1:
                            if "begin_time" in h['hours'][0]    and "end_time" in h['hours'][0]:
                                time = h['hours'][0]['begin_time']+ ' '+ h['hours'][0]['end_time']
                            else:
                                time ="<MISSING>"
                            
                        # exit()
                        tem_var.append("https://www.target.ca")
                        tem_var.append(j['location_names'][0]['name'] if j['location_names'][0]['name'] else "<MISSING>" )
                        tem_var.append(j['address']['address_line1']if j['address']['address_line1'] else "<MISSING>" )
                        tem_var.append(j['address']['city'].strip() if j['address']['city'].strip() else "<MISSING>")
                        tem_var.append(j['address']['region'] if j['address']['region'] else "<MISSING>")
                

                        tem_var.append(j['address']['postal_code'] if j['address']['postal_code']  else "<MISSING>")
                        tem_var.append("US")
                        tem_var.append("<MISSING>")
                        
                        tem_var.append(j['contact_information']['telephone_number'] if j['contact_information']['telephone_number'] else "<MISSING>")
                        tem_var.append("target")
                        tem_var.append(j['geographic_specifications']['latitude'] if j['geographic_specifications']['latitude'] else "<MISSING>" )
                        tem_var.append(j['geographic_specifications']['longitude'] if j['geographic_specifications']['longitude'] else "<MISSING>" )
                        tem_var.append(time if time else "<MISSING>" )
                        
                        if tem_var[3] in addresses:
                            continue
                        addresses.append(tem_var[3])
                        return_main_object.append(tem_var) 
        except:
            continue
        
    return return_main_object


            

def scrape():
    data = fetch_data()
    write_output(data)


scrape()



