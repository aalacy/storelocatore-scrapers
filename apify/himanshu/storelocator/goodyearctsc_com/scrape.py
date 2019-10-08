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
                'https://gyfleethqservices.com/api/Dealer/DealerSearch?dealerSearchParameters.milesRadius=100&dealerSearchParameters.latitude='+ zip_code[0]+'&dealerSearchParameters.longitude='+zip_code[1]+'&api_key=vdUHnhNUY95w3OiVgugndw7Z2VGwBkUgTaQuLozc35gj2alKoaKbk3yKWFm5Edjy8tTJSYXO94K+9UnjaJBUnw==',
                headers=headers,
        
            )
            soup= BeautifulSoup(r.text,"lxml")
            k = json.loads(soup.text)
            
            # if k !=[]:
            time =''
            if k != None and k !=[]:
                for i in k:
                    tem_var=[]
                    if 'hours' in i and i['hours'] !=None:
                        for j in i['hours']:
                            time = time +' ' +(j['day']+ ' '+j['formattedTime'])
                    else:
                        time = ''

                    tem_var.append("https://www.goodyearctsc.com")
                    tem_var.append(i['name'] if i['name'] else "<MISSING>" )
                    tem_var.append(i['streetAddress'].strip().replace('--','<MISSING>') if i['streetAddress'].strip()  else "<MISSING>" )
                    tem_var.append(i['city'].strip() if i['city'].strip() else "<MISSING>")
                    tem_var.append(i['state'] if i['state'] else "<MISSING>")
                    if len(i['zip'])==6 or len(i['zip'])==7:
                        c = 'CA'
                    else:
                        c = "US"

                    tem_var.append(i['zip'] if i['zip'] else "<MISSING>")
                    tem_var.append(c)
                    tem_var.append("<MISSING>")
                    
                    tem_var.append(i['phoneFormatted'] if i['phoneFormatted'] else "<MISSING>")
                    tem_var.append("goodyearctsc")
                    tem_var.append(i['geoLocation']['latitude'] if i['geoLocation']['latitude'] else "<MISSING>" )
                    tem_var.append(i['geoLocation']['longitude'] if i['geoLocation']['longitude'] else "<MISSING>" )
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



