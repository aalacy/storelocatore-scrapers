# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json,urllib
import time
import lxml


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url1 = "https://www.wyndhamhotels.com"
    base_url = "https://www.wyndhamhotels.com/baymont/locations"
    r = session.get(base_url)
    main_soup = BeautifulSoup(r.text,"lxml")
    k = main_soup.find_all('li',{'class':'property'})

    store_name = []
    store_detail = []
    for link  in k:
        temp_var = []
        r = session.get(base_url1+str(link.a['href']))
        soup = BeautifulSoup(r.text,"lxml")
        scripts =soup.find_all('script')
        for script in scripts:
            if re.search("var overview_lat",script.text):
                myString = re.sub(r"[\n\t\s]*", "", script.text)
                id1 = re.findall('\d+',myString.split(';')[0]) 
                for j in id1:
                    url = "https://www.wyndhamhotels.com/BWSServices/services/search/property/search?propertyId="+ j +"&isOverviewNeeded=true&isAmenitiesNeeded=true&channelId=tab&language=en-us" 
                    lm_json = session.get(url).json()
                        
                    if "checkInTime" in lm_json['properties'][0] or "checkOutTime" in lm_json['properties'][0]:
                            if lm_json['properties'][0]['checkInTime']:
                                checkInTime1 = int(lm_json['properties'][0]['checkInTime'].replace(' ',''))
                                # checkInTime1 = (int(checkInTime1)/100%12)
                                # checkInTime1 = "%2d:00" %(checkInTime1)
                            else:
                                checkInTime1 = "<MISSING>"

                            if lm_json['properties'][0]['checkOutTime']:
                                checkOutTime1 = int(lm_json['properties'][0]['checkOutTime'])
                                # checkOutTime1 =  int(checkOutTime1)/100%12 
                                # checkOutTime1 = "%2d:00" %(checkOutTime1)
                            else:
                                checkOutTime1 = "<MISSING>"
                    
                    

        data1 = json.loads(soup.find('script', type='application/ld+json').text,strict=False)
        name = data1['name']
        store_name.append(name)

        streetAddress = data1['address']['streetAddress']
        city =  data1['address']['addressLocality']
        
        if "addressRegion" in data1['address']:
            state =  data1['address']['addressRegion']
        else:
            state = "<MISSING>"

        if "postalCode" in data1['address']:
            zipcord =  data1['address']['postalCode']
            if len(zipcord) == 6 or len(zipcord) == 7:
                    country_code1 = "CA"
            else:
                    country_code1 = "US"
        else:
            zipcord =  "<MISSING>" 

        country_code = country_code1
        store_number = "<MISSING>"
        phone = data1['telephone']
        location_type = "<MISSING>"
        latitude = data1['geo']['latitude']
        longitude = data1['geo']['longitude']
        hours_of_operation = str(checkInTime1)+ ' ' +str(checkOutTime1)
        temp_var.append(streetAddress)
        temp_var.append(city)
        temp_var.append(state)
        temp_var.append(zipcord)
        temp_var.append(country_code)
        temp_var.append(store_number)
        temp_var.append(phone)
        temp_var.append(location_type)
        temp_var.append(latitude)
        temp_var.append(longitude)
        temp_var.append(hours_of_operation)
        store_detail.append(temp_var)

    return_main_object = []


    for i in range(len(store_name)):
        store= list()
        store.append("https://www.wyndhamhotels.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    return return_main_object



def scrape():
    data = fetch_data()
    write_output(data)

scrape()

