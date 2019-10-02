import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

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
    address5 =[]
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
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 1000
    MAX_DISTANCE = 200000
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()    # zip_code = search.next_zip()  

    while coord:
        base_url = 'https://storelocator.officedepot.com/ajax?xml_request=<request><appkey>AC2AD3C2-C08F-11E1-8600-DCAD4D48D7F4</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>250</limit><geolocs><geoloc><addressline>33496</addressline><longitude>'+str(coord[1])+'</longitude><latitude>'+str(coord[0])+'</latitude></geoloc></geolocs><searchradius>20|35|50|100|250</searchradius><where><or><nowdocs><eq></eq></nowdocs><expanded_furn><eq></eq></expanded_furn><usps><eq></eq></usps><shredding><eq></eq></shredding><selfservews><eq></eq></selfservews><photoprint><eq></eq></photoprint><expandedbb><eq></eq></expandedbb><warranty_carry><eq></eq></warranty_carry><cellphonerepair><in></in></cellphonerepair><techtradein><eq></eq></techtradein><techrecycling><eq></eq></techrecycling><techzone><eq></eq></techzone><selfservprinting><eq></eq></selfservprinting><usps_mail><eq></eq></usps_mail></or><icon><eq></eq></icon></where></formdata></request>'
        try:
            r = requests.get(base_url)
            soup= BeautifulSoup(r.text,"lxml")

        
            tem_var =[]
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
                    # print(i)
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
                new_list=[]
                new_list.append(address2[i])
                new_list.append(city2[i])
                new_list.append(state2[i])
                new_list.append(postalcode2[i])
                new_list.append(country2[i])
                new_list.append(store_no2[i])
                new_list.append(phone2[i])
                new_list.append("<MISSING>")
                new_list.append(latitude2[i])
                new_list.append(longitude2[i])
                new_list.append(hours2[i])
                if new_list[2] in address5:
                    continue
            
                address5.append(new_list[2])

                # print(new_list)
                store_detail.append(new_list)
            
            coord = search.next_coord()
 
        except:
            continue

    store_name[15] ='1570 N FEDERAL HWY'
    

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.officedepot.com")  
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append("https://www.officedepot.com/storelocator/findStore.do")
        return_main_object.append(store)
    
    return return_main_object


  


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
