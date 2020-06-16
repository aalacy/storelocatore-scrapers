import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import requests
session = SgRequests()
# deere


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    adressess = []
    response={}
    base_url = "https://www.deere.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    for i in ['18', '19', '20', '21', '27', '28']:
        url ="https://dealerlocator.deere.com/servlet/ajax/getLocations?lat=33.597346&long=-112.107252&locale=en_US&country=US&uom=MI&filterElement="+str(i)
        # url = "https://dealerlocator.deere.com/servlet/ajax/getLocations?lat="+str(coord[0])+"&long="+str(coord[0])+"&locale=en_US&country=US&uom=MI&filterElement=18"
        try:
            response = requests.get( url, headers=headers).json()
        except:
            pass
        if "locations" in response:
            for data in response['locations']:
                latitude = data['latitude']
                longitude = data['longitude']
                location_name = data['locationName']
                page_url = data['seoFriendlyUrl']
                street_address = " ".join(data['formattedAddress'][:-1])
                zipp = data['formattedAddress'][-1].split( )[-1]
                state = data['formattedAddress'][-1].split( )[-2]
                city = " ".join(data['formattedAddress'][-1].split( )[:-2])
                phone = data['contactDetail']['phone']
                store_number = "<MISSING>"
                hours=""
                # if data['OpeningHours'] != None:
                #     for h in data['OpeningHours']:
                #         # print(h)
                #         if h["Value"] != None:
                #             if h["Value"]:
                #                 hours = hours+ ' '+h["Label"]+ ' '+h["Value"]
                # else:
                hours = "<MISSING>"
                if len(zipp) != 5:
                    index = 5
                    char = '-'
                    zipp = zipp[:index] + char + zipp[index + 1:]
                    # print(zipp)
                store = [] 
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)   
                store.append("US")
                store.append(store_number)
                store.append(phone)
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours if hours else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")     
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                if store[2] in adressess:
                    continue
                adressess.append(store[2])
                # print(store)
                yield store

    for i in ['18', '19', '20', '21', '27', '28']:
        url ="https://dealerlocator.deere.com/servlet/ajax/getLocations?lat=47.569907&long=-52.695462&locale=en_GB&country=CA&uom=KM&filterElement="+str(i)
        # url = "https://dealerlocator.deere.com/servlet/ajax/getLocations?lat="+str(coord[0])+"&long="+str(coord[0])+"&locale=en_US&country=US&uom=MI&filterElement=18"
        try:
            response = requests.get( url, headers=headers).json()
        except:
            pass
        if "locations" in response:
            for data in response['locations']:
                latitude = data['latitude']
                longitude = data['longitude']
                location_name = data['locationName']
                page_url = data['seoFriendlyUrl']
                street_address = " ".join(data['formattedAddress'][:-1])
                zipp = data['formattedAddress'][-1].split( )[-1]
                # print( data['formattedAddress'][-1].split(""))
                # state = data['formattedAddress'][-1].split( )[-2]
                city = " ".join(data['formattedAddress'][-1].split( )[:-2])
                phone = data['contactDetail']['phone']
                store_number = "<MISSING>"
                hours=""
                # if data['OpeningHours'] != None:
                #     for h in data['OpeningHours']:
                #         # print(h)
                #         if h["Value"] != None:
                #             if h["Value"]:
                #                 hours = hours+ ' '+h["Label"]+ ' '+h["Value"]
                # else:
                hours = "<MISSING>"
                store = []
                state_list = re.findall(r' ([A-Z]{2})', str(data['formattedAddress'][-1]))
                if state_list:
                    state = state_list[-1]
                city = data['formattedAddress'][-1].split(state)[0]
                zipp = data['formattedAddress'][-1].split(state)[-1]
                # print( data['formattedAddress'][-1].split(state))
                # print(state)
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)   
                store.append("CA")
                store.append(store_number)
                store.append(phone)
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours if hours else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")     
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                if store[2] in adressess:
                    continue
                adressess.append(store[2])
                # print(store)
                yield store

     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
