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

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addressess = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ["UK"])
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
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
        # print("zip_code === "+zip_code)
        # result_coords.append((latitude, longitude))
        location_url = "https://www.onestop.co.uk/wp-admin/admin-ajax.php"

        
        try:
            data = requests.post(location_url,data=data,headers=headers ).json()
        except:
            pass
        # soup = BeautifulSoup(data.text, "lxml")
        # print(soup)
        # current_results_len = len(data['message']['results'])

        # print("data===",data['message']['results'])

        # print("location_url ==== "+location_url)

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
        # print("data['message']['results'] ", type(data['message']['results']))
        # try:
        try:
            locations = data['message']['results']
            current_results_len = len(data['message']['results'])
        except:
            locations = []


        for loc in locations:
            street_address = loc['location']['contact']["address"]['lines'][-1]['text']
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
                        # print(str(loc['location']['openingHours'][-1]['standardOpeningHours'][loc1]['open']))
                        # print("-===-----------------------------=-=-=-=--=-=-=-=-=-=-=-==-==--=")
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
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        # except:
        #     pass



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
