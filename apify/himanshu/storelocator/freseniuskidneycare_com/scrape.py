import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def request_wrapper(url,method,headers,data=None):
   request_counter = 0
   if method == "get":
       while True:
           try:
               r = requests.get(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   elif method == "post":
       while True:
           try:
               if data:
                   r = requests.post(url,headers=headers,data=data)
               else:
                   r = requests.post(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   else:
       return None      

def fetch_data():
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    country_code = "US"
    base_url = "https://www.freseniuskidneycare.com/"
    locator_domain = base_url
    location_type = ""
    # lat = coord[0]
    # lng = coord[1]
    for i in range(1,281):
       # print(i)
        location_url = "https://www.freseniuskidneycare.com/dialysis-centers?lat=39.3096984&lng=-76.6701475&address=Baltimore,%20MD%2021216,%20USA&radius=10000&page=" + str(i)
        k = request_wrapper(location_url,"get",headers=headers)
        soup = BeautifulSoup(k.text,"lxml")
        # data = soup.find_all("script",{'type':"application/ld+json"})[2:].text
        for i in soup.find_all("script",{'type':"application/ld+json"})[2:]:
            text = i.text
            json_data = json.loads(text)
            if "address" in json_data:
                store_number = "<MISSING>"
                if "geo" in json_data :
                    if "latitude" in json_data['geo']:
                        latitude = json_data['geo']['latitude']
                    else:
                        latitude = "<MISSING>"
                    if "longitude" in json_data['geo']:
                        longitude = json_data['geo']['longitude']
                    else:
                        longitude = "<MISSING>"
                else:
                    latitude="<MISSING>"
                    longitude ="<MISSING>"
                if "name" in json_data:
                    location_name = json_data['name'] 
                else:
                    location_name = "<MISSING>"
                if "address" in json_data:
                    if "addressLocality" in json_data['address']:
                        city = json_data['address']['addressLocality'] 
                    else:
                        city = "<MISSING>"
                    if "addressRegion" in json_data['address']:
                        state = json_data['address']['addressRegion']
                    else:
                        state = "<MISSING>"
                    if "postalCode" in json_data['address']:
                        zipp = json_data['address']['postalCode']
                    else:
                        zipp = "<MISSING>"
                else:
                    street_address ="<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                if "telephone" in json_data:
                    phone = json_data['telephone']
                else:
                    phone = "<MISSING>"
                if "@type" in json_data:
                    location_type = json_data['@type'] 
                else:
                    location_type = "<MISSING>"
                if "openingHours" in json_data:
                    hours_of_operation = "  ".join(json_data['openingHours'])
                else:
                    hours_of_operation = "<MISSING>"
                if "url" in json_data:
                    page_url = json_data['url']
                    k1 = request_wrapper(page_url,"get",headers=headers)
                    soup1 = BeautifulSoup(k1.text,"lxml")
                    data1 = soup1.find_all("p",{'class':"locator-text"})[1].find("span")
                    street_address1 = (data1.text.replace("\n","").replace("\r","").replace("\t","").strip().lstrip().rstrip())
                    street_address = street_address1.replace("                                   "," ")
                store = [locator_domain, location_name.encode('ascii', 'ignore').decode('ascii').strip(), street_address.encode('ascii', 'ignore').decode('ascii').strip(), city.encode('ascii', 'ignore').decode('ascii').strip(), state.encode('ascii', 'ignore').decode('ascii').strip(), zipp.encode('ascii', 'ignore').decode('ascii').strip(), country_code,
                            store_number, phone.encode('ascii', 'ignore').decode('ascii').strip(), location_type, latitude, longitude, hours_of_operation.replace("hours", "").encode('ascii', 'ignore').decode('ascii').strip(), page_url]
                if str(store[2]) + str(store[-3]) not in addresses:
                    addresses.append(str(store[2]) + str(store[-3]))
                    store = [x if x else "<MISSING>" for x in store]
                    yield store





def scrape():
    data = fetch_data()
    write_output(data)
scrape()
