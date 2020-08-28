import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime

session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    
    base_url = "https://www.caferouge.com/"
    json_data = session.get("https://api.casualdininggroup.uk/pagedata?brandKey=caferouge&path=/spaces/hlvdy7x28mmo/entries?access_token=bad26202af27c0f9ca3921ab7fb67bc6eea2b34ba73fe53168bf041548707f8c%26select=fields.title,fields.slug,fields.city,fields.addressLocation,fields.addressLine1,fields.addressLine2,fields.addressCity,fields.county,fields.postCode,fields.storeId,fields.eeRestaurantId,fields.services,fields.amenities,fields.hours,fields.alternativeHours,fields.takeawayDeliveryServices,fields.heroTile,fields.phoneNumber,fields.bookingProviderUrl,fields.takeawayCollectionService,fields.collectionMessage%26content_type=restaurant%26include=10%26limit=1000").json()

    for data in json_data['items']:
        data = data['fields']
        location_name = data['title']
        street_address = data['addressLine1']
        if "addressLine2" in data and  data['addressLine2']:
            street_address += data['addressLine2']
        city = data['addressCity']
        state = data['county']
        zipp = data['postCode']
        store_number = data['storeId']
        phone = data['phoneNumber']
        lat = data['addressLocation']['lat']
        lng = data['addressLocation']['lon']

        page_url = "https://www.caferouge.com/bistro-brasserie/"+str(data['city'])+"/"+str(data['slug'])
        hours_json = session.get("https://api.casualdininggroup.uk/pagedata?brandKey=caferouge&path=/spaces/hlvdy7x28mmo/entries?access_token=bad26202af27c0f9ca3921ab7fb67bc6eea2b34ba73fe53168bf041548707f8c%26select=fields.title,fields.slug,fields.city,fields.heroTile,fields.description,fields.addressLocation,fields.deliverooLink,fields.email,fields.phoneNumber,fields.amenities,fields.miscellaneous,fields.metaTags,fields.metaTagsForBookNowTab,fields.imageGallery,fields.promotionStack,fields.offersTitle,fields.offersDescription,fields.eeRestaurantId,fields.eventSection,fields.takeawayCollectionService,fields.takeawayDeliveryServices,fields.storeId,fields.addressLine1,fields.addressLine2,fields.addressCity,fields.county,fields.postCode,fields.hours,fields.alternativeHours,fields.takeATourUrl,fields.bookingProviderUrl,fields.collectionMessage%26content_type=restaurant%26fields.slug="+str(data['slug'])+"%26fields.city="+str(data['city'])+"%26include=10").json()
        
        hours = ''
        for hr in hours_json['includes']['Entry']:
            hr = hr['fields']
            if "mondayOpen" in hr:
                
                hours = "Monday "+ hr['mondayOpen'] +"-" + hr['mondayClose']  \
                    +" Tuesday "+ hr['tuesdayOpen'] +"-" + hr['tuesdayClose'] \
                    +" Wednesday "+ hr['wednesdayOpen'] +"-" + hr['wednesdayClose'] \
                    +" Thursday " + hr['thursdayOpen'] +"-" + hr['thursdayClose'] \
                    +" Friday "+ hr['fridayOpen'] +"-" + hr['fridayClose'] \
                    +" Saturday "+ hr['saturdayOpen'] +"-" + hr['saturdayClose'] \
                    +" Sunday "+ hr['sundayOpen'] +"-" + hr['sundayClose']
        
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("UK")
        store.append(store_number)
        store.append(phone)
        store.append("CAFE ROUGE")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
        
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
