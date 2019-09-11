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
        'clientKey': 'lVqTrQx76FnGUhV6AFi7iSy9aXRwLIy7',
        'clientKey': 'lVqTrQx76FnGUhV6AFi7iSy9aXRwLIy7',
        'Sec-Fetch-Mode': 'cors',
        'apiKey': 'PZUJEgLI2AwEeY3imkqxG2LOgELG3hVd'
  
        
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

        r = requests.get(
            'https://us.nissan-api.net/v2/dealers?size=50&lat='+ zip_code[0]+'&long='+ zip_code[1]+'&serviceFilterType=AND&include=openingHours',
            headers=headers,
       
        )
        soup= BeautifulSoup(r.text,"lxml")
        k = json.loads(soup.text)
        if 'dealers' in k:
            for i in k['dealers']:
                tem_var=[]
                # print(i['departments']['sales']['hours']['sunday']['open']['time'] + ' '+i['departments']['sales']['hours']['sunday']['close']['time'])
                # hours = 'sunday' +' '+i['departments']['sales']['hours']['sunday']['open']['time'] + ' '+i['departments']['sales']['hours']['sunday']['close']['time']+ ' '+'monday'+' '+i['departments']['sales']['hours']['monday']['open']['time'] + ' '+i['departments']['sales']['hours']['monday']['close']['time']+ ' '+ 'tuesday'+' '+i['departments']['sales']['hours']['tuesday']['open']['time'] + ' '+i['departments']['sales']['hours']['tuesday']['close']['time']+' '+'wednesday'+' '+i['departments']['sales']['hours']['wednesday']['open']['time'] + ' '+i['departments']['sales']['hours']['wednesday']['close']['time']+' '+'thursday'+' '+i['departments']['sales']['hours']['thursday']['open']['time'] + ' '+i['departments']['sales']['hours']['thursday']['close']['time']+' '+'friday'+' '+i['departments']['sales']['hours']['friday']['open']['time'] + ' '+i['departments']['sales']['hours']['friday']['close']['time']+ ' '+'saturday'+' '+i['departments']['sales']['hours']['saturday']['open']['time'] + ' '+i['departments']['sales']['hours']['saturday']['close']['time']
  
                if len(i['address']['postalCode'])==6 or len(i['address']['postalCode'])==7:
                    c = "CA"
                else:
                    c= "US"

                # if  len(i['address']['postalCode'])==9:
                #     word = ['address']['postalCode']
                #     index = 5
                #     char = '-'
                #     zip1 = word[:index] + char + word[index + 1:]
                h1 =  i['openingHours']['regularOpeningHours']
                time1 = (i['openingHours']['openingHoursText'].replace("\n",' '))
                time =''
                for h in h1:

                    if 'openIntervals' in h:
                        h2 = ('openFrom'+ ' '+h['openIntervals'][0]['openFrom'] + ' ' + 'openUntil'+ ' '+h['openIntervals'][0]['openUntil'])
                    else:
                        h2 = str(h['closed'])
                    
                    time = time  + ' ' + h2
                hours = (time +' '+time1)
                # exit()
                tem_var.append("https://www.infinitiusa.com/")
                tem_var.append(i['name'])
                tem_var.append(i['address']['addressLine1'])
                tem_var.append(i['address']['city'])
                tem_var.append(i['address']['stateCode'])
                tem_var.append(i['address']['postalCode'])
                tem_var.append(c)
                tem_var.append('<MISSING>')
                tem_var.append(i['contact']['phone'])
                tem_var.append("infinitiusa")
                tem_var.append(i['geolocation']['latitude'])
                tem_var.append(i['geolocation']['longitude'])
                tem_var.append(hours)
                
                if tem_var[3] in address:
                    continue

                address.append(tem_var[3])

                return_main_object.append(tem_var) 

    
    return return_main_object


            

def scrape():
    data = fetch_data()
    write_output(data)


scrape()



