# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addressesess = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    store_list=[]
    MAX_RESULTS = 100
    MAX_DISTANCE = 20
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }


    while coord:
        result_coords = []
        # print("ramiang zip =====" + str(search.current_zip))
        lat = coord[0]
        lng = coord[1]
        addresses =[]
        address2=[]
        city2=[]
        state2 =[]
        postalcode2=[]
        country2=[]
        store_no2=[]
        phone2=[]
        latitude2=[]
        longitude2=[]
        mons2=[]
        tuess2=[]
        wed2=[]
        thu2=[]
        fri2=[]
        sat2=[]
        sun2=[]
        hours2=[]
        return_main_object =[]
        store_detail =[]
        store_name=[]



        location_url = 'https://storelocator.officedepot.com/ajax?&xml_request=<request><appkey>AC2AD3C2-C08F-11E1-8600-DCAD4D48D7F4</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>250</limit><geolocs><geoloc><addressline>'+str(search.current_zip)+'</addressline><longitude>'+str(lng)+'</longitude><latitude>'+str(lat)+'</latitude></geoloc></geolocs><searchradius>'+str(MAX_DISTANCE)+'</searchradius><where><or><nowdocs><eq></eq></nowdocs><expanded_furn><eq></eq></expanded_furn><usps><eq></eq></usps><shredding><eq></eq></shredding><selfservews><eq></eq></selfservews><photoprint><eq></eq></photoprint><expandedbb><eq></eq></expandedbb><warranty_carry><eq></eq></warranty_carry><cellphonerepair><in></in></cellphonerepair><techtradein><eq></eq></techtradein><techrecycling><eq></eq></techrecycling><techzone><eq></eq></techzone><selfservprinting><eq></eq></selfservprinting><usps_mail><eq></eq></usps_mail><coworking><eq></eq></coworking></or><icon><eq></eq></icon></where></formdata></request>'
        try:
            r = requests.get(location_url, headers=headers)
        except:
            pass
        # r_utf = r.text.encode('ascii', 'ignore').decode('ascii')
        soup = BeautifulSoup(r.text, "lxml")
        location_type = soup.find_all("poi")
        names =  soup.find_all("address2")
        address1 = soup.find_all("address1")
        state1 = soup.find_all("state")
        city1 = soup.find_all("city")
        postalcode1= soup.find_all("postalcode")
        countrys =  soup.find_all('country')
        store_no1 = soup.find_all("clientkey")
        phones = soup.find_all('phone')
        latitude1 = soup.find_all("latitude")
        longitude1 = soup.find_all("longitude")
        
        mons = soup.find_all("mon")
        tuess = soup.find_all("tues")
        wed1 = soup.find_all("wed")
        thu1 =  soup.find_all("thur")
        fri1 = soup.find_all("fri")
        sat1 = soup.find_all("sat")
        sun1 = soup.find_all("sun")
     
        current_results_len = int(len(address1))  # it always need to set total len of record.      
        for mon in mons:
            mons2.append(mon.text)
        for tues in tuess:
            tuess2.append(tues.text)
        for wed in  wed1:
            wed2.append(wed.text)
        for thu in thu1:
            thu2.append(thu.text)
        for fri in fri1:
            fri2.append(fri.text)
        for sat in sat1:
            sat2.append(sat.text)
        for sun in sun1:
            sun2.append(sun.text)

        for j in range(len(mons2)):
            hours=''
            time =[]
            time.append( " mon "+ mons2[j] + ' tues '+ tuess2[j] + ' wed '+ wed2[j] + ' thur ' + thu2[j] + ' fri ' +fri2[j] + ' sat ' + sat2[j] + ' sun ' + sun2[j])
            for i in time:
                hours = hours+ ' ' +i
            hours2.append(hours)
        

        for address in address1:
            address2.append(address.text)
        for city in city1:
            city2.append(city.text)
        for state in state1:
            state2.append(state.text)
        for postalcode in postalcode1:
            postalcode2.append(postalcode.text)
        for country in countrys:
            country2.append(country.text)
        for store_no in store_no1:
            store_no2.append(store_no.text)   
        for phone in phones:
            phone2.append(phone.text)
        for latitude in latitude1:
            latitude2.append(latitude.text)
        for longitude in longitude1:
            longitude2.append(longitude.text)
        for add in names:
            store_name.append(add.text)
        
        for i in range(len(address2)):
            locator_domain = ("https://www.officedepot.com")
            location_name = store_name[i] if store_name[i] else "<MISSING>" 
            street_address = (address2[i])
            city = (city2[i])
            state = (state2[i])
            zipp = postalcode2[i]
            country_code = (country2[i])
            store_number = (store_no2[i])
            phone = (phone2[i])
            try:
                location_type1 = location_type[i].find("icon").text.strip()
            except:
                location_type1 = location_type[i].find("name").text.strip()
            latitude = (latitude2[i])
            longitude = (longitude2[i])
            hours_of_operation = (hours2[i].strip())
            page_url = "<MISSING>"
            result_coords.append((latitude, longitude))
            store_list1 = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type1, latitude, longitude, hours_of_operation,page_url]

            if store_list1[2] in addressesess:
                continue
            addressesess.append(store_list1[2])
            yield store_list1
            # print(store_list1) 
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
     
def scrape():
    data = fetch_data()
    write_output(data)


scrape()

