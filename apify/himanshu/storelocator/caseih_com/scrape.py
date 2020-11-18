import csv
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('caseih_com')




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
    MAX_RESULTS = 50
    MAX_DISTANCE = 40
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['US',"CA"])
    coord = search.next_coord()
    current_results_len = 0
    adressess = []

    base_url = "https://www.caseih.com/"
    while coord:
        result_coords =[]
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        response={}
        if len(str(search.current_zip))==5:
            contry="US"
            url = "https://www.caseih.com/northamerica/en-us/_layouts/15/CaseIH/Dealers.aspx?country=US&latitude="+str(coord[0])+"&longitude="+str(coord[1])
        else:
            contry="CA"
            url="https://www.caseih.com/northamerica/en-us/_layouts/15/CaseIH/Dealers.aspx?country=CA&latitude="+str(coord[0])+"&longitude="+str(coord[1])
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        "x-requested-with":"XMLHttpRequest",
        "accept:":"*/*"
        }
        try:
            response = requests.get(url).json()
        except:
            pass
        try:
            if "results" in response['data'] and response['data']['results'] != None :
                for data in response['data']['results']:
                    street_address=data['Address']
                    street_address1=data['Address1']
                    street_address2=data['Address2']
                    street_address3=data['Address3']
                    street_address_n=''
                    if street_address:
                        street_address =street_address
                    else:
                        street_address=''
                    if street_address1:
                        street_address1 = street_address1
                    else:
                        street_address1=''
                    if street_address2:
                        street_address2 = street_address2
                    else:
                        street_address2=''
                    if street_address3:
                        street_address3 = street_address3
                    else:
                        street_address3=''
                    street_address_n = street_address + ' '+street_address1+ ' '+ street_address2+ ' '+street_address3
                    location_name = data['Name']
                    hours="<MISSING>"
                    city = data['City']
                    state = data['State']
                    zipp = str(data['PostalCode'])
                    if len(str(data['PostalCode']))==9:
                        index = 5
                        char = '-'
                        zipp = zipp[:index] + char + zipp[index + 1:]
                    phone = data['Telephone']
                    lat = data['Latitude']
                    lng = data['Longitude']
                    name = data['Name']
                    store_number = data['Id']
                    sun=data['DealerShipAttributes']['sundayAMStart']
                    sun1=data['DealerShipAttributes']['sundayPMEnd']
                    if sun != None and sun1 != None:
                        sunday = " Sunday: "+sun+' - '+sun1
                    else:
                        sunday = "Sunday: Close "
                    page_url = 'https://www.caseih.com/northamerica/en-us/pages/dealer-landing-page.aspx?idDealer='+str(store_number)
                    # logger.info(page_url)
                    # response1 = bs(requests.get(page_url).text,'lxml')
                    # hours_of_operation=''
                    # try:
                    #     hours_of_operation=" ".join(list(response1.find("ul",{"class":"dealer-hours"}).stripped_strings))
                    # except:
                    #     hours_of_operation=" ".join(list(response1.find("ul",{"class":"dealer-hours"}).stripped_strings))
                    hours=''
                    mon1 = data['DealerShipAttributes']['mondayAMStart']
                    mon2 = data['DealerShipAttributes']['mondayPMEnd']
                    if  mon1 != None and mon2 != None:
                        mon = " Monday: "+mon1+' - '+ mon2
                    else:
                        mon = "Monday: Close "
                    tue1 = data['DealerShipAttributes']['tuesdayAMStart']
                    tue2 = data['DealerShipAttributes']['tuesdayPMEnd']
                    if  tue1 != None and tue2 != None:
                        tue = " Tuesday: "+tue1+' - '+ tue2
                    else:
                        tue = " Tuesday: Close "
                    wed1 = data['DealerShipAttributes']['wednesdayAMStart'] 
                    wed2 = data['DealerShipAttributes']['wednesdayPMEnd']
                    if wed1 != None and wed2 != None:
                        wed = " Wednesday: "+ wed1 +' - '+ wed2
                    else:
                        wed = " Wednesday: Close"
                    thue1 = data['DealerShipAttributes']['thursdayAMStart']
                    thue2 = data['DealerShipAttributes']['thursdayPMEnd']
                    if  thue1  != None and thue2:
                        thue = " Thursday: "+ thue1+' - '+ thue2
                    else:
                        thue = " Thursday: Close"
                    fri1 = data['DealerShipAttributes']['fridayAMStart']
                    fri2 = data['DealerShipAttributes']['fridayPMEnd']
                    if  fri1 != None and fri2 != None:
                        fri = " Friday: "+fri1+' - '+ fri2
                    else:
                        fri = " Friday: Close"
                    sat1 =data['DealerShipAttributes']['saturdayAMStart']
                    sat2 = data['DealerShipAttributes']['saturdayPMEnd']
                    if  sat2 != None and sat1:
                        sat = " Saturday: "+sat1+' - '+ sat2
                    else:
                        sat = " Saturday: Close "
                    hours = mon + tue + wed + thue + fri + sat +sunday
                    # logger.info(data['DealerShipAttributes']['mondayAMStart'])
                    result_coords.append((lat,lng))
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address_n.strip())
                    store.append(city)
                    store.append(state)
                    store.append(zipp)   
                    store.append(contry)
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append("<MISSING>")
                    store.append(lat)
                    store.append(lng)
                    store.append(hours.replace("Monday: Close  Tuesday: Close  Wednesday: Close Thursday: Close Friday: Close Saturday: Close Sunday: Close",'<MISSING>') if hours else "<MISSING>")
                    store.append(page_url if page_url else "<MISSING>")     
                    store = [str(x).strip() if x else "<MISSING>" for x in store]
                    if street_address_n.strip() in adressess:
                        continue
                    adressess.append(street_address_n.strip())
                    # logger.info(store)
                    yield store
        except:
            pass
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        
        coord = search.next_coord()
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
