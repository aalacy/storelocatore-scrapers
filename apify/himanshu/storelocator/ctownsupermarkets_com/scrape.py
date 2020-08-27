import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time 
from datetime import datetime
import time
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)
def request_wrapper(url,method,headers,data=None):
   request_counter = 0
   if method == "get":
       while True:
           try:
               r = session.get(url,headers=headers)
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
                   r = session.post(url,headers=headers,data=data)
               else:
                   r = session.post(url,headers=headers)
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
    return_main_object = []
    address = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     
    zip_code = search.next_zip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://ctownsupermarkets.com"
    while zip_code:
        result_coords = []
        location_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=50&location=%22"+str(zip_code)+"%22&limit=25&api_key=ae29ff051811d0bf52d721ab2cadccb8&v=20181201&resolvePlaceholders=true&entityTypes=location&savedFilterIds=29721495"
        r = session.get(location_url,headers=headers)
        #print(location_url)
        data = (r.text)
        json_data = json.loads(data)
        k = (json_data['response']['entities'])
        for i in k:
            page_url = i['landingPageUrl']
            #print(page_url)
            r = request_wrapper(page_url,"get",headers=headers)
            soup = BeautifulSoup(r.text,"lxml")
            data = soup.find("script",{"type":"application/ld+json"})
            mp = str(data).split("</script>")[0].split('application/ld+json">')[1]
            json_data = json.loads(mp)
            street_address = json_data['address']['streetAddress']
            city = json_data['address']['addressLocality']
            state = json_data['address']['addressRegion']
            zipp =json_data['address']['postalCode']
            country_code = i['address']['countryCode']
            latitude = json_data['geo']['latitude']
            longitude = json_data['geo']['longitude']
            page_url= json_data['url']
            store_number = json_data['@id'].split("_")[1]
            phone = json_data['telephone']
            location_type = json_data['@type'][0]
            location_name = json_data['name']
            hours_of_operation1 = json_data['openingHoursSpecification']
            hours_of_operation =''
            for mp1 in hours_of_operation1:
                if "dayOfWeek" in mp1:
                    start_time = datetime.strptime(mp1['opens'], "%H:%M").strftime("%I:%M %p")
                    end_time = datetime.strptime(mp1['closes'], "%H:%M").strftime("%I:%M %p")
                    hours_of_operation += mp1['dayOfWeek'] +" "+str(start_time)+" - "+str(end_time)+" "
                else:
                    soup = BeautifulSoup(session.get(page_url).text,"lxml")
                    try:
                        hours_of_operation = " ".join(list(soup.find("tbody",{"class":"hours-body"}).stripped_strings))
                    except:
                        hours_of_operation = "<MISSING>"
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else"<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            yield store 
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
