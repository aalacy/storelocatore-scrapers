import csv
import requests
from bs4 import BeautifulSoup
import re
# import http.client
import sgzip
import json
# import  pprint
import time

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
    base_url = "https://www.bylinebank.com"
    # conn = http.client.HTTPSConnection("guess.radius8.com")

    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 80
    coords = search.next_coord()
    current_results_len = 0
    # search.current_zip """"""""==zip
    header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
              "Content-Type":"application/x-www-form-urlencoded",
               "Referer": "https://bylinebank.locatorsearch.com/index.aspx?s=FCS"
              }
    while coords:
        # try:
        result_coords = []
        url = 'https://bylinebank.locatorsearch.com/GetItems.aspx'
        data = "lat="+str(coords[0])+"&lng="+str(coords[1])+"&searchby=FCS%7C&SearchKey=&rnd=1569844320549"
        
        # pagereq = request_wrapper(url,"post",data=data, headers=header)
        # if pagereq==None:
        #     continue
        # print("==============",coords)
        s = requests.Session()
        try:
            r= requests.post(
                'https://bylinebank.locatorsearch.com/GetItems.aspx',
                headers=header,data=data,
            )
        except:
            continue


        country_code="US"
        pagereq = s.get(url,data=data, headers=header)
        soup = BeautifulSoup(pagereq.content, 'html.parser')
        add2 = soup.find_all("add2")
        address1 = soup.find_all("add1")
        loc = soup.find_all("marker")
        current_results_len = len(loc)
        hours = soup.find_all("contents")
        name = soup.find_all("title")
        
        locator_domain = "https://www.bylinebank.com"
        store_number ="<MISSING>"
        location_type ='<MISSING>'
        # print(soup)
        for i in range(len(address1)):
            street_address = address1[i].text
            city = add2[i].text.replace("<br>",",").replace("<b>","").replace("</b>","").strip().split(",")[0]
            state = add2[i].text.replace("<br>",",").replace("<b>","").replace("</b>","").strip().split(",")[1].split( )[0]
            zip1 = add2[i].text.replace("<br>",",").replace("<b>","").replace("</b>","").strip().split(",")[1].split( )[1]
            phone = add2[i].text.replace("<br>",",").replace("<b>","").replace("</b>","").strip().split(",")[2]
            try:
                location_name = name[i].text.replace("<br>","")
                # .split(">")[1].replace("</a", "")
            except:
                location_name ='<MISSING>'

            # print(location_name)

            if len(zip1)==6 or len(zip1)==7:
                country_code = "CA"
            else:
                country_code = "US"
            if "Monday:" in hours[i].text:
                soup_hour = BeautifulSoup(hours[i].text,'lxml')
                h = []
                for tr in soup_hour.find('table').find_all('tr'):
                    list_tr = list(tr.stripped_strings)
                    if len(list_tr) ==1:
                        hour = "<MISSING>"
                    else:
                        hour = " ".join(list_tr)
                    h.append(hour)
                if "<MISSING>"  in " ".join(h):
                    hours_of_operation = "<MISSING>"

                else:
                    hours_of_operation = "  ".join(h)
              
            latitude = loc[i].attrs['lat']
            longitude = loc[i].attrs['lng']
            result_coords.append((latitude,longitude))
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name.encode('ascii', 'ignore').decode('ascii').strip() if location_name else '<MISSING>')
            store.append(street_address.encode('ascii', 'ignore').decode('ascii').strip() if street_address else '<MISSING>')
            store.append(city.encode('ascii', 'ignore').decode('ascii').strip() if city else '<MISSING>')
            store.append(state.encode('ascii', 'ignore').decode('ascii').strip() if state else '<MISSING>')
            store.append(zip1.encode('ascii', 'ignore').decode('ascii').strip() if zip1 else '<MISSING>')
            store.append(country_code.encode('ascii', 'ignore').decode('ascii').strip() if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone.encode('ascii', 'ignore').decode('ascii').strip() if phone else '<MISSING>')
            store.append(location_type.encode('ascii', 'ignore').decode('ascii').strip() if location_type else '<MISSING>')
            store.append(latitude.encode('ascii', 'ignore').decode('ascii').strip() if latitude else '<MISSING>')
            store.append(longitude.encode('ascii', 'ignore').decode('ascii').strip() if longitude else '<MISSING>')
            store.append(hours_of_operation.encode('ascii', 'ignore').decode('ascii').strip() if hours_of_operation else '<MISSING>')
            store.append("<MISSING>")
            if store[2] in addresses:
                continue
            addresses.append(store[2])

            #print("data = " + str(store))
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
      
        coords = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
