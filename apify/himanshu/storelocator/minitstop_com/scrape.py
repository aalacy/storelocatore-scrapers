import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

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
    
    base_url = "http://hawaiipetroleum.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")

    return_main_object =[]
    store_detail =[]
    store_name=[]
    info = soup.find_all("div",{"class":"wpgmza-content-address-holder"})
    dk = {}
    for id,val in enumerate(soup.find_all('script')):
        if id == 150:

            json_data = json.loads(val.text.split('var wpgmaps_localize_marker_data = ')[1].split(';')[0])

            for id,val in enumerate(json_data):
                for key in  json_data[val].keys():
                    # print(json_data[val][key])
                    dk[json_data[val][key]['title']]= [json_data[val][key]['lat'],json_data[val][key]['lng']]
                # for
                # print(json_data[val].keys())

                # print(val.text.split('var wpgmaps_localize_marker_data = '))
                # exit()



    for i in info:
        tem_var=[]

        if len(list(i.stripped_strings)) ==6:
            location_name = list(i.stripped_strings)[0]
            store_name.append(list(i.stripped_strings)[0])

            street_address1 = list(i.stripped_strings)[2]
            street_address = street_address1.replace("\n","").split(',')[0]
            city = street_address1.replace("\n","").split(',')[1]
            state =street_address1.replace("\n","").split(',')[2].split( )[0]
            zipcode = street_address1.replace("\n","").split(',')[2].split( )[1]
            hours_of_operation = list(i.stripped_strings)[3]
            phone = list(i.stripped_strings)[4].replace("Tel: ","")
            lat = '<MISSING>'
            lng = '<MISSING>'
            if location_name in dk:
                lat = dk[location_name][0]
                lng  = dk[location_name][1]

            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")

            tem_var.append(lat)
            tem_var.append(lng)
            tem_var.append(hours_of_operation)
            tem_var.append(base_url)

            store_detail.append(tem_var)
            
        elif len(list(i.stripped_strings)) ==4:
            location_name = list(i.stripped_strings)[0]
            store_name.append(list(i.stripped_strings)[0])
            street_address1 = list(i.stripped_strings)[2].split(',')[0]
            city = list(i.stripped_strings)[2].split(',')[1]
            state = list(i.stripped_strings)[2].split(',')[2].split( )[0]
            zipcode = list(i.stripped_strings)[2].split(',')[2].split( )[1]
            hours_of_operation ="<MISSING>"
            lat = '<MISSING>'
            lng = '<MISSING>'
            if location_name in dk:
                lat = dk[location_name][0]
                lng = dk[location_name][1]
            

            tem_var.append(street_address1)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(lat)
            tem_var.append(lng)
            tem_var.append(hours_of_operation)
            tem_var.append(base_url)

            store_detail.append(tem_var)
            
            

        elif len(list(i.stripped_strings)) ==5:
            location_name = list(i.stripped_strings)[0]
            street_address1 = list(i.stripped_strings)[2]
            store_name.append(list(i.stripped_strings)[0])
            
            hours_of_operation= list(i.stripped_strings)[3]
            if street_address1.count(',') ==3:
                st = street_address1.split(',')
                st[0] = " ".join(st[0:2])
                del st[1]
                street_address = st[0]
                city =st[1]
                state = st[2].split( )[0]
                zipcode = st[2].split( )[1]
                lat = '<MISSING>'
                lng = '<MISSING>'
                if location_name in dk:
                    lat = dk[location_name][0]
                    lng = dk[location_name][1]

                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(lat)
                tem_var.append(lng)
                tem_var.append(hours_of_operation)
                tem_var.append(base_url)

                store_detail.append(tem_var)
                
            else:
                st = street_address1.split(',')[0]
                city =street_address1.split(',')[1]
                state = street_address1.split(',')[2].split( )[0]
                zipcode = street_address1.split(',')[2].split( )[1]

                lat = '<MISSING>'
                lng = '<MISSING>'
                if location_name in dk:
                    lat = dk[location_name][0]
                    lng = dk[location_name][1]

                tem_var.append(st)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(lat)
                tem_var.append(lng)
                tem_var.append(hours_of_operation)
                tem_var.append(base_url)

                store_detail.append(tem_var)
                
                
                

        elif len(list(i.stripped_strings)) ==9:
            location_name = list(i.stripped_strings)[0]
            store_name.append(list(i.stripped_strings)[0])
            hours_of_operation = list(i.stripped_strings)[4]
            street_address = list(i.stripped_strings)[2].split(',')[0]
            city = list(i.stripped_strings)[2].split(',')[1]
            state =list(i.stripped_strings)[2].split(',')[2].split( )[0]
            zipcode =list(i.stripped_strings)[2].split(',')[2].split( )[1]
            phone = list(i.stripped_strings)[3].replace("Tel: ","")

            lat = '<MISSING>'
            lng = '<MISSING>'
            if location_name in dk:
                lat = dk[location_name][0]
                lng = dk[location_name][1]

            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(lat)
            tem_var.append(lng)
            tem_var.append(hours_of_operation)
            tem_var.append(base_url)

            store_detail.append(tem_var)
            
    for i in range(len(store_name)):
        store = list()
        store.append("https://hawaiipetroleum.com")

        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    print(return_main_object)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
