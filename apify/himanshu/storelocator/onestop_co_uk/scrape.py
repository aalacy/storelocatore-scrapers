import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import datetime
from datetime import datetime

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    return_main_object = []
    addressess = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ["UK"])
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     
    zip_code = search.next_zip()
    base_url = "https://www.onestop.co.uk/"
    while zip_code:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            "Referer": "https://www.onestop.co.uk/store-finder/?search="+str(zip_code),
            "Content-type": "application/x-www-form-urlencoded",
            "Host": "www.onestop.co.uk",
        }
        result_coords = []
        data = "action=findstockists&searchfor="+str(zip_code)
        location_url = "https://www.onestop.co.uk/wp-admin/admin-ajax.php"
        try:
            data = requests.post(location_url,data=data,headers=headers ).json()
        except:
            pass
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "UK"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        try:
            locations = data['message']['results']
            current_results_len = len(data['message']['results'])
        except:
            locations = []
        for loc in locations:
            street_address1 = loc['location']['contact']["address"]['lines'][-1]['text'].replace("300 Lancaster Road","").replace("98-102 Poulton Road","").replace("294-296 Poulton Road","").replace("1-2 Newmarket Green","").replace("165-171 New Cross Road","").replace("161 Fernside Avenue","").replace("32-34 Lord Street","")
            street_address2 = loc['location']['contact']["address"]['lines'][0]['text'].replace("32-34 New Bank Road","").replace("1861 Paisley Road West","").replace("137-139 Lancaster Road","").replace("125 Denmark Hill","").replace("14-16 High Street","").replace("81-83 Weatherhill Road","").replace("12 Everingham Road","").replace("2-4 King Edward Road","").replace("90 Warmsworth Road","").replace("122-124 Sandford Road","").replace("55 Carr House Road","").replace("252 King Cross Road","").replace("2 Granny Hall Lane","").replace("161 Fernside Avenue","").replace("15 Broad Lane","").replace("81-83 Weatherhill Road","")
            street_address = (street_address2 + street_address1).replace("Unit 10, Local Centre Retail Park, Pioneer WayKingswood","672-674 Marfleet Lane").replace("<MISSING>","161 Fernside Avenue")
            city = loc['location']['contact']["address"]['town']
            zipp = loc['location']['contact']["address"]['postcode']
            page_url = "https://www.onestop.co.uk/store/?store="+zipp.lower().replace(" ",'')
            latitude = loc['location']['geo']['coordinates']['latitude']
            longitude = loc['location']['geo']['coordinates']['longitude']
            result_coords.append((latitude, longitude))
            if "phoneNumbers" in loc['location']['contact']:
                phone =  loc['location']['contact']['phoneNumbers'][-1]['number']
            hours_of_operation = ''
            if "openingHours" in loc['location']:
                for loc1 in loc['location']['openingHours'][-1]['standardOpeningHours']:
                    timeopen = loc['location']['openingHours'][-1]['standardOpeningHours'][loc1]['open']
                    timeclose = loc['location']['openingHours'][-1]['standardOpeningHours'][loc1]['close']
                    if loc['location']['openingHours'][-1]['standardOpeningHours'][loc1]['isOpen']=="true" and timeopen != "0000" and timeclose != "0000":
                        
                        d = datetime.strptime(str(timeopen), "%H%M")
                        opentime =d.strftime("%I:%M %p")
                        d1 = datetime.strptime(str(timeclose), "%H%M")
                        close = d1.strftime("%I:%M %p")
                        hours_of_operation = hours_of_operation+ ' '+ loc1 + ' '+ opentime + ' '+close
                    else:
                        hours_of_operation = hours_of_operation + ' '+loc1 + ' close '
            store = [locator_domain, loc['location']['name'], street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, str(latitude), str(longitude), hours_of_operation,page_url]

            if store[2]  in addressess:
                continue
            addressess.append(store[2])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in  store]

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
