import csv
import time

from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'application/vnd.puro.locator+json'

    }

    addresses = []
    return_main_object=[] 
    base_url = 'https://api.purolator.com/'
    r = session.get("https://api.purolator.com/locator/puro/json/location/byCoordinates/53.541047/-113.581174?radialDistanceInKM=50&holdForPickup=false&dangerousGoods=false&kiosk=false&streetAccess=false&wheelChairAccess=false&maxNumberofLocations=30&openTime=01:00:00&closeTime=20:00:00&currentlyOpen=true&gmtOffset=05:00:00&locationType=Staples&locationType=ShippingCentre&locationType=ShippingAgent&locationType=DropBox&locationType=MobileQuickStop&locationType=QuickStopKiosk&locationType=QuickStopAgent&dayOfWeek=Sunday&dayOfWeek=Monday&dayOfWeek=Tuesday&dayOfWeek=Wednesday&dayOfWeek=Thursday&dayOfWeek=Friday&dayOfWeek=Saturday", headers=headers).json()
    k = r['locations']
    for i in k:
        tem_var =[]
        phone=i['phoneNumber']
        location_name=i['locationName']
        location_type=i['locationType']
        address = i['address']['streetNumber']+' '+i['address']['streetName']+' '+i['address']['streetType']
        latitude = i['latitude']
        longitude = i['longitude']
        city = i['address']['municipalityName']
        country_code=i['address']['countryCode']
        zip = i['address']['postalCode'] 
        state= i['address']['provinceCode']
        hour1= i['hoursOfOperation']
        time =''
        for i in hour1:

            time = time + ' '+ i['day'] + ' '+i['open'] +' '+i['close']
        print(time)
        tem_var.append(base_url)
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append(zip)
        tem_var.append(country_code)
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append(location_type)
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append(time)
        tem_var.append('<MISSING>')
        return_main_object.append(tem_var)
                  
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
