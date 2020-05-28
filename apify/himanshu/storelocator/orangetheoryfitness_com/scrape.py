import csv
from bs4 import BeautifulSoup
import re
import json
import requests

ca_state_abbr = {
    "BC" : "British Columbia", 
    "ON" : "Ontario", 
    "NL" : "Newfoundland and Labrador", 
    "NS" : "Nova Scotia", 
    "PE" : "Prince Edward Island", 
    "NB" : "New Brunswick", 
    "QC" : "Quebec", 
    "MB" : "Manitoba", 
    "SK" : "Saskatchewan", 
    "AB" : "Alberta", 
    "NT" : "Northwest Territories", 
    "NU" : "Nunavut",
    "YT" : "Yukon Territory",
    "NFLD" :"Newfoundland and Labrador"
}
state_slug_list = []
s_abbr = []
s_name = []
for key,value in ca_state_abbr.items():
    s_abbr.append(key)
    s_name.append(value)


def write_output(data):
    with open('data.csv', mode='w',newline='', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    locator_domain = "https://www.orangetheory.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    for country in ["United+States","Canada"]:
        base_url=  "https://www.orangetheory.com/bin/otf/studios?latitude=26.4029696&longitude=-80.1172975&distance=10000&country="+str(country)+"&sort=studioName" 
        r = requests.get(base_url)   
        json_data = r.json()
        for j in json_data['data']:
            for i in j:
                base_url = "https://www.orangetheory.com/"
                hours_of_operation = "<MISSING>"
                store_number = i['studioId']
                street_address = i['studioLocation']['physicalAddress'].replace("\r\n","")
                city  = i['studioLocation']['physicalCity'].strip()
                state  =  i['studioLocation']['physicalState']
                zipp  = i['studioLocation']['physicalPostalCode']
                latitude   = str(i['studioLocation']['latitude']).strip()
                longitude  = str(i['studioLocation']['longitude']).strip()
                if latitude == "1" or longitude == "1":
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                location_name = i['studioName']
                if "United States" == i['studioLocation']['physicalCountry'].strip():
                    country_code =  "US"
                else :
                    country_code = "CA"
                if i['studioLocation']['phoneNumber']:
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(i['studioLocation']['phoneNumber']))
                    if phone_list:
                        phone = phone_list[0]
                    else:
                        phone = "<MISSING>"
                else:
                    phone = "<MISSING>"
                location_type ="Orangetheory Fitness"
                street_slug = [re.sub(r"[^a-zA-Z0-9]+", ' ', k) for k in street_address.split("\n")]
                city_slug = [re.sub(r"[^a-zA-Z0-9]+", ' ', k) for k in city.split("\n")]
                                
                if country_code == "CA":
                    page_url = ""
                    if city and state and street_address != "<MISSING>":
                        for i in  range(len(s_abbr)):
                            if state.strip() == s_abbr[i].strip():
                                state_slug = s_name[i].strip().lower().replace(" ","-")
                                page_url = "https://www.orangetheory.com/en-ca/locations/"+str(state_slug)+"/"+str(" ".join(city_slug).strip().lower().replace(" ","-").strip())+"/"+str(" ".join(street_slug).strip().lower().replace(" ","-").strip())+"/"
                                if "3055 West Broadway" == str(" ".join(street_slug)).strip():
                                    page_url = "https://www.orangetheory.com/en-ca/locations/"+str(state_slug)+"/"+str(" ".join(city_slug).strip().lower().replace(" ","-").strip())+"/"+str(" ".join(street_slug).strip().lower().replace(" ","-").replace("3055","3097").strip())+"rn"+city.lower()+"-"+state.lower()+"-"+zipp.replace(" ","-").lower()+"/"
                                if "102 11510 Westgate Drive" == str(" ".join(street_slug)).strip():
                                    page_url = "https://www.orangetheory.com/en-ca/locations/"+str(state_slug)+"/grand-prairie/unit-102-11510-westgate-dr/"
                                if "107 1171 Marine Drive" == str(" ".join(street_slug)).strip():
                                    page_url = "https://www.orangetheory.com/en-ca/locations/"+str(state_slug)+"/"+str(" ".join(city_slug).strip().lower().replace(" ","-").strip())+"/1171-marine-drive-107/"
                                if "2945 Jacklin Road Unit 133" == str(" ".join(street_slug)).strip():
                                    page_url = "https://www.orangetheory.com/en-ca/locations/"+str(state_slug)+"/langford/unit-133-2956-jacklin-road/"
                                if "400 Capilano Road Unit 11" ==str(" ".join(street_slug)).strip():
                                    page_url = "https://www.orangetheory.com/en-ca/locations/"+str(state_slug)+"/"+str(" ".join(city_slug).strip().lower().replace(" ","-").strip())+"/"+str(" ".join(street_slug).strip().replace("Unit ","").lower().replace(" ","-").strip())+"/"
                                if "135 12101 72 Avenue" == str(" ".join(street_slug)).strip():
                                    page_url = "https://www.orangetheory.com/en-ca/locations/"+str(state_slug)+"/"+str(" ".join(city_slug).strip().lower().replace(" ","-").strip())+"/135-1210172-ave/"
                                
                                    # print(page_url) 
                                # print(state_slug," | "+str(" ".join(city_slug))+" | "+str(" ".join(street_slug)))
                                # print(page_url)
                                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    else:
                        page_url = "<MISSING>"
                else:
                    if city and state and street_address != "<MISSING>":
                        page_url = "https://www.orangetheory.com/en-us/locations/"+str(state).lower().replace(" ","-").strip()+"/"+str(" ".join(city_slug).strip().lower().replace(" ","-").strip())+"/"+str(" ".join(street_slug).strip().lower().replace(" ","-").strip())+"/"   
                    else:
                        page_url = "<MISSING>"
                hours_of_operation = "<MISSING>"
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                if (str(store[1])+" "+str(store[2])) not in addresses:
                    addresses.append((str(store[1])+" "+str(store[2])))

                    # print("data = " + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
