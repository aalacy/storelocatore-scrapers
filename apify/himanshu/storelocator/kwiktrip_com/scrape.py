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
    # zips = sgzip.for_radius(100)
    zips = sgzip.coords_for_radius(50)

    
    return_main_object = []
    addresses = []
    store_name=[]
    store_detail=[]
  

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "content-type": "application/json;charset=UTF-8",
  
        
    }

    address=[]
    for zip_code in zips:   
        try :
 
            r = requests.get(
                'https://www.kwiktrip.com/locproxy.php?Latitude='+zip_code[0]+'&Longitude='+zip_code[1] +'&maxDistance=100000&limit=100',
                headers=headers,
        
            )
            soup= BeautifulSoup(r.text,"lxml")
            
            
            k = json.loads(soup.text)
            if len(k) != 1 or k in 'stores':
                for i in k['stores']:
                    # print(i['address']['address1'])
                    tem_var=[]
                    tem_var.append("https://www.kwiktrip.com")
                    tem_var.append(i['name'])
                    tem_var.append(i['address']['address1'])
                    tem_var.append(i['address']['city'])
                    tem_var.append(i['address']['state'])
                    tem_var.append(i['address']['zip'])
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(i['phone'])
                    tem_var.append("kwiktrip")
                    tem_var.append(i['latitude'])
                    tem_var.append(i['longitude'])
                    tem_var.append('<MISSING>')
                    print(tem_var)
                    
                    # if i['open24Hours']=='true':
                    #     tem_var.append('open24Hours')
                    # else:
                    #     print(zip_code)
                    #     print(i['open24Hours'])
                    # print(tem_var)
                    if tem_var[3] in address:
                        continue

                    address.append(tem_var[3])

                    return_main_object.append(tem_var) 
        except:
            continue
    
    return return_main_object


            

def scrape():
    data = fetch_data()
    write_output(data)


scrape()



