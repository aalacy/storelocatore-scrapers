import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
# import time


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    zips = sgzip.for_radius(50)



    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',

        'content-type': "application/json",
        'accept': "*/*",
        'cache-control': "no-cache"

    }

    # it will used in store data.
    locator_domain = "https://www.pga.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    url = "https://api.pga.com/graphql"
    for zip_code in zips:
        try:
            loc_url = "https://www.pga.com/play/search?searchText="+str(zip_code)
            r_page = requests.get(loc_url,headers = headers)
            soup = BeautifulSoup(r_page.text,'lxml')
            div = soup.find('div',class_='MuiGrid-root MuiGrid-container MuiGrid-spacing-xs-2')
            link = []
            for a in  div.find_all('a'):
                p_url  = a['href']
                link.append(p_url)
            # print(link)

        except:
            continue
        payload = "{\"operationName\":\"SearchCourses\",\"variables\":{\"searchText\":\""+str(zip_code)+"\"},\"query\":\"query SearchCourses($searchText: String!) {\\n  searchCourses(searchText: $searchText) {\\n    name\\n    photo_facility\\n    facility_id\\n    city\\n    state\\n    zip\\n    address1\\n    address2\\n    __typename\\n  }\\n}\\n\"}"

        try:
            response = requests.request("POST", url, data=payload, headers=headers)
            json_data = response.json()
        except:
            continue

        if json_data['data']['searchCourses'] != None:
            for loc in json_data['data']['searchCourses']:
                facility_id= loc['facility_id']
                payload1 = "{\"operationName\":\"Facility\",\"variables\":{\"id\":\""+str(facility_id)+"\"},\"query\":\"query Facility($id: String!) {\\n  facility(facility_id: $id) {\\n    facility_id\\n    facility_name\\n    state\\n    state_name\\n    city\\n    zip\\n    phone\\n    photo_facility\\n    course_type_label\\n    address1\\n    address2\\n    address3\\n    address4\\n    universal_id\\n    members {\\n      name\\n      photo_profile\\n      universal_id\\n      member_class_description\\n      member_class\\n      member_type\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"}"
                try:
                    r = requests.request("POST", url, data=payload1, headers=headers)
                    r_data = r.json()
                except:
                    continue
                store_number = r_data['data']['facility']['facility_id']

                location_name = r_data['data']['facility']['facility_name']
                street_address = r_data['data']['facility']['address1']
                city = r_data['data']['facility']['city']
                state = r_data['data']['facility']['state']
                zipp_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(r_data['data']['facility']['zip']))
                if zipp_list == []:
                    zipp = "<MISSING>"
                else:
                    zipp= zipp_list[0].strip()
                # print(zipp,state,street_address)


                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(r_data['data']['facility']['phone']))
                if phone_list  !=  []:
                    phone = phone_list[0].strip().replace(')','')
                else:
                    phone = "<MISSING>"
                # print(state + " | "+zipp)
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                if link != []:
                    page_url = "https://www.pga.com"+link.pop(0)
                else:
                    pass
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                store = ["<MISSING>" if x == ""  or x== None else x for x in store]
                if store_number in addresses:
                    continue
                addresses.append(store_number)

                #print("data = " + str(store))
                #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()

