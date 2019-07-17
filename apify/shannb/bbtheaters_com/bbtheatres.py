import requests
from bs4 import BeautifulSoup
import csv
import xlsxwriter
#from geopy.geocoders import Nominatim
#from geopy.exc import GeocoderTimedOut
#import time

base_url = 'https://bbtheatres.com'
locations_url = base_url + '/locations'


def get_lat_long(address):

    geolocator = Nominatim(user_agent="scraper")
    location = None
    try:
        
        location = geolocator.geocode(address)
    except GeocoderTimedOut:
        time.sleep(30)
        location = geolocator.geocode(address)

    if location:
        return (location.latitude, location.longitude)
    else:
        return None

def write_to_file(theater_list):

     with open('bbtheaters.csv', 'w') as csvfile:
        field_names = ["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"]

        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        for theater in theater_list:

            writer.writerow({"locator_domain": theater["locator_domain"],
                                "location_name" : theater["location_name"],
                                "street_address" : theater["street_address"],
                                "city" : theater["city"],
                                "state" : theater["state"],
                                "zip" : theater["zip"],
                                "country_code" : theater["country_code"],
                                "store_number" : theater["store_number"],
                                "phone" : theater["phone"],
                                "location_type" : theater["location_type"],
                                "latitude" : theater["latitude"],
                                "longitude" : theater["longitude"],
                                "hours_of_operation" : theater["hours_of_operation"]
                                })



soup = BeautifulSoup(requests.get(locations_url).content, 'html.parser').find(id="locations-houses")

theater_list = []

for location in soup:

    theater = {}
    theater["locator_domain"] = base_url + location['href']
    
    contents = location.find(class_="theater-box").contents 
    theater["street_address"] = contents[2].strip("\n\t\t\t\t\t\t\t")
    theater["location_name"] = contents[1].text
    theater["phone"] = contents[6].strip("Movie Info: ").strip("\n\t\t\t\t\t  \t")
    address = contents[4].split(",")
    theater["city"] = address[0]
    theater["state"] = address[1].split(" ")[1]
    theater["zip"] = address[1].split(" ")[2].strip("\n\t\t\t\t\t\t\t")
    theater["country_code"] = "US"
   
    theater["latitude"] = "<MISSING>"
    theater["longitude"] = "<MISSING>"
    theater["store_number"] = "<MISSING>"
    theater["location_type"] = "<MISSING>"
    theater["hours_of_operation"] = "<MISSING>"
    

    theater_list.append(theater)

write_to_file(theater_list)