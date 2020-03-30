import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


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
    base_url = "https://www.cort.com"
    r = session.get(base_url+"/locations")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    output=[]
    main=soup.find('script',{"id":"cort-state"}).text.split('&q;cortDisplayName&q;:&q;')
    del main[0]
    for data in main:
        loclick=data.split('&q;,')[0]
        link=data.split('&q;id&q;:&q;')[1].split('&q;,')[0]
        if link !="/CORT":
            if loclick not in output:
                output.append(loclick)
                loc = session.get(base_url+"/public/v1/storelocator/"+link.strip()).json()
                address=loc['addressLine1']
                if address:
                    if loc['addressLine2']:
                        address+=' '+loc['addressLine2']
                    hour=' '
                    if loc['storeHours']['mondayOpen']:
                        d="-"+loc['storeHours']['mondayOpen'] if loc['storeHours']['mondayClose'] else ''
                        hour+="Monday : "+loc['storeHours']['mondayOpen']+ d 
                    if loc['storeHours']['tuesdayOpen']:
                        d="-"+loc['storeHours']['tuesdayOpen'] if loc['storeHours']['tuesdayClose'] else ''
                        hour+="Tuesday : "+loc['storeHours']['tuesdayOpen']+ d 
                    if loc['storeHours']['wednesdayOpen']:
                        d="-"+loc['storeHours']['wednesdayOpen'] if loc['storeHours']['wednesdayClose'] else ''
                        hour+="Wednesday : "+loc['storeHours']['wednesdayOpen']+ d 
                    if loc['storeHours']['thursdayOpen']:
                        d="-"+loc['storeHours']['thursdayOpen'] if loc['storeHours']['thursdayClose'] else ''
                        hour+="Thursday : "+loc['storeHours']['thursdayOpen']+ d
                    if loc['storeHours']['fridayOpen']:
                        d="-"+loc['storeHours']['fridayOpen'] if loc['storeHours']['fridayClose'] else ''
                        hour+="Friday : "+loc['storeHours']['fridayOpen']+ d
                    if loc['storeHours']['saturdayOpen']:
                        d="-"+loc['storeHours']['saturdayOpen'] if loc['storeHours']['saturdayClose'] else ''
                        hour+="Saturday : "+loc['storeHours']['saturdayOpen']+ d 
                    if loc['storeHours']['sundayOpen']:
                        d="-"+loc['storeHours']['sundayOpen'] if loc['storeHours']['sundayClose'] else ''
                        hour+="Sunday : "+loc['storeHours']['sundayOpen']+ d 
                    store=[]
                    store.append(base_url)
                    store.append(loc['typeDisplayName'])
                    store.append(address)
                    store.append(loc['city'])
                    store.append(loc['state'])
                    store.append(loc['postalCode'])
                    store.append("US")
                    store.append(loc['id'])
                    store.append(loc['phoneNumber'])
                    store.append("Cort")
                    store.append(loc['latitude'])
                    store.append(loc['longitude'])
                    if hour.strip():
                        store.append(hour.strip())
                    else:
                        store.append("<MISSING>")
                    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
