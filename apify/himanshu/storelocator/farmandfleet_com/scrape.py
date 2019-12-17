import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import urllib.parse
import time
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
    base_url = "https://www.farmandfleet.com"


    # print("start")
    addresses = []
    

    addresses = []
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              "X-Distil-Ajax": "dsvsxzeu",
              'Content-type': 'application/x-www-form-urlencoded',
              "Accept": "*/*",
              "Content-Length": "17",
            #   "Content-Type": "application/json;charset=UTF-8",
              "Host": "www.farmandfleet.com",
                # "Cookie":"VSID=nt=AzmPlJwPfXSV6DgnJBsxIA==&dt=Xh4Rdj0vDYKye+tGxYFBdDMDY7CruKybntKjP1I+ThI=&i=5/ovkax6y1KpM2RNxf9JE6cmrzpz5U8n7ZG/crEtp0npgj0I6bHZLbbiA1mZMIck&bk=5/ovkax6y1KpM2RNxf9JE6cmrzpz5U8n7ZG/crEtp0npgj0I6bHZLbbiA1mZMIck; SFN=; NoEAlerts=1; visitor_id=b1aed5eb-94f0-40f2-84a5-d76b7e58c4d7; visit_id=9067da85-44ea-4f8c-8d31-e1efc84ec24f; _gcl_au=1.1.1625190482.1575366134; D_IID=147670F1-7155-304C-81D6-4DCC0D6B9488; D_UID=F6DE9AA8-3694-3A9E-B04D-8E79D077EB04; D_ZID=38CEABF6-A9E3-395F-BBE8-A413BFFFC7CA; D_ZUID=0F7A6E2F-B234-39B0-8BEA-64DAFC98280E; D_HID=2997B0ED-321D-32C2-A409-798C13A137D0; D_SID=45.56.148.75:5wlUwM7LyVL31Km6DK+UxqYyrXy1h4G4/tyoAGEyH/g; cto_lwid=750ed5b0-b40a-4414-9025-38d2dee628bd; _ga=GA1.2.1291904524.1575366136; _gid=GA1.2.1601315190.1575366136; _fbp=fb.1.1575366137000.2070915611; rskxRunCookie=0; rCookie=ou1sqy72fc7jimtp0ucayk3pobpts; stc120352=tsa:1575366137421.610100718.8157496.3408764118433447.1:20191203101421|env:1%7C20200103094217%7C20191203101421%7C2%7C1098738:20201202094421|uid:1575366137420.520290699.51840734.120352.2023026843:20201202094421|srchist:1098738%3A1%3A20200103094217:20201202094421; SFV=c=12/3/2019 5:15:41 AM; Loc=s=0&z=07094&t=0&o=0; _dc_gtm_UA-193719-1=1; lastRskxRun=1575371819277",
              "Origin": "https://www.farmandfleet.com",
              "Referer": "https://www.farmandfleet.com/store-finder/"

              
              
              }
    
    while zip_code:
        # print(zip_code)
        
        result_coords = []
        data = "query="+str(zip_code)
        # driver = get_driver()
        # data = '{"query":"'+str("85029")+'"}'
     
        r = requests.post('https://www.farmandfleet.com/store-finder/a/find', headers=header, data=data).json()
        # for loc in data:
        #     print(loc['address1'])
        # print(soup.text.split("window.headerJson")[1].replace(" = ","").replace("};","}"))
        # exit()

       
        if r != False:
            current_results_len =len(r)
            for id,val in enumerate(r):
                locator_domain = base_url
                location_name =  val['textHeader']
                street_address = val['address1']
                city = val['city']
                state =  val['state']
                zip =  val['zip']
                country_code = 'US'
                store_number = val['storeNum']
                phone = ''
                if 'phone' in val:
                    phone = val['phone']
                location_type ="<MISSING>"
                # location_type = base_url+'/stores/'+val['urlAlias']
                latitude = val['latitude']
                longitude = val['longitude']
                # val['LocationType']
                types = "<MISSING>"
                # print(types)
                page_url = val['urlAlias']
                hours_of_operation1=''
                if "currentAutomotiveCenterHours" in val and val['currentAutomotiveCenterHours'] != None:
                    hours_of_operation1 ='Automotive Service Hours'+ ' '+ ' monday: ' + val['currentAutomotiveCenterHours']['mondayOpen'] +' : '+ val['currentAutomotiveCenterHours']['mondayClose'] + ' tuesday ' +  val['currentAutomotiveCenterHours']['tuesdayOpen'] + ' : ' + val['currentAutomotiveCenterHours']['tuesdayClose'] + ' wednesday ' + val['currentAutomotiveCenterHours']['wednesdayOpen'] +  ' : ' + val['currentAutomotiveCenterHours']['wednesdayOpen'] + ' thursday ' + val['currentAutomotiveCenterHours']['thursdayOpen'] + ' : ' + val['currentAutomotiveCenterHours']['tuesdayClose'] + ' friday ' + val['currentAutomotiveCenterHours']['fridayOpen'] +  ' : ' + val['currentAutomotiveCenterHours']['fridayClose'] + ' saturday ' + val['currentAutomotiveCenterHours']['saturdayOpen'] + ' : '+ val['currentAutomotiveCenterHours']['saturdayClose'] +'sunday'+val['currentAutomotiveCenterHours']['sundayOpen'] + ' : ' + val['currentAutomotiveCenterHours']['sundayClose']
                # else:
                #     hours_of_operation1 = "<MISSSING>"


                # print(val['hours']['tue'][0])
               
                kk = []
                hours_of_operation = 'Store Hours'+ ' '+' monday: ' + val['currentHours']['mondayOpen'] +' : '+ val['currentHours']['mondayClose'] + ' tuesday ' +  val['currentHours']['tuesdayOpen'] + ' : ' + val['currentHours']['tuesdayClose'] + ' wednesday ' + val['currentHours']['wednesdayOpen'] +  ' : ' + val['currentHours']['wednesdayOpen'] + ' thursday ' + val['currentHours']['thursdayOpen'] + ' : ' + val['currentHours']['tuesdayClose'] + ' friday ' + val['currentHours']['fridayOpen'] +  ' : ' + val['currentHours']['fridayClose'] + ' saturday ' + val['currentHours']['saturdayOpen'] + ' : '+ val['currentHours']['saturdayClose'] +'sunday'+val['currentHours']['sundayOpen'] + ' : ' + val['currentHours']['sundayClose']
                if street_address in addresses:
                    continue
                addresses.append(street_address)
                store = []
                result_coords.append((latitude, longitude))
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zip if zip else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(hours_of_operation+ ' ' + hours_of_operation1 if hours_of_operation+ ' ' + hours_of_operation1 else '<MISSING>')
                store.append( base_url+'/stores/'+val['urlAlias'])
                #print("===", str(store))
                # return_main_object.append(store)
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

    # coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
