import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)

def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url, headers=headers)
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
                    r = requests.post(url, headers=headers, data=data)
                else:
                    r = requests.post(url, headers=headers)
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
    addresses = []
    search = sgzip.ClosestNSearch()
    # search.initialize(country_codes=[‘us’, ‘ca’])
    search.initialize(include_canadian_fsas=True)
    MAX_RESULTS = 1000000
    MAX_DISTANCE = 25
    # current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()
    # coord = search.next_coord()
    result_coords = []

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data.
    locator_domain = "https://www.truevaluecompany.com/"
    page_url = "<MISSING>"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    while zip_code:
        result_coords = []

        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))

        base_url = "https://www.truevaluecompany.com"
        # time.sleep(1)
        try:
            r = request_wrapper('https://hosted.where2getit.com/truevalue/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E41C97F66-D0FF-11DD-8143-EF6F37ABAA09%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E' + str(zip_code) +
                                '%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E10%7C25%7C50%7C100%7C250%3C%2Fsearchradius%3E%3Cwhere%3E%3Cor%3E%3Ctv%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftv%3E%3Chg%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fhg%3E%3Cgr%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fgr%3E%3Cds%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fds%3E%3Cja%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fja%3E%3Ctaylorrental%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftaylorrental%3E%3C%2For%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E', "get", headers=headers)

            soup = BeautifulSoup(r.text, 'lxml')

            main = soup.find_all('poi')
            current_results_len = len(str(main))
            # print(main)
            # print(current_results_len)
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            for poi in main:
                name = poi.find('name').text.strip().capitalize()
                address = poi.find('address1').text.strip().capitalize()
                city = poi.find('city').text.strip().capitalize()
                country = poi.find('country').text.strip()
                if country not in ["US", "CA"]:
                    continue
                # print(country)
                state = poi.find('state').text.strip()
                lat = poi.find('latitude').text.strip()
                lng = poi.find('longitude').text.strip()
                phone = poi.find('phone').text.strip()
                zip = poi.find('postalcode').text.strip()
                if "00000-0000" == zip:
                    zip = "<MISSING>"
                else:
                    zip = zip
                # print(zip, country)
                if "11732-1601" == zip:
                    country = "CA"

                hour = ''
                if poi.find('mon_open_time').text.strip():
                    hour += " Monday : " + \
                        poi.find('mon_open_time').text.strip() + \
                        poi.find('mon_close_time').text.strip()
                if poi.find('tue_open_time').text.strip():
                    hour += " Tuesday : " + \
                        poi.find('tue_open_time').text.strip() + \
                        poi.find('tue_close_time').text.strip()
                if poi.find('wed_open_time').text.strip():
                    hour += " Wednesday : " + \
                        poi.find('wed_open_time').text.strip() + \
                        poi.find('wed_close_time').text.strip()
                if poi.find('thur_open_time').text.strip():
                    hour += " Thursday : " + \
                        poi.find('thur_open_time').text.strip() + \
                        poi.find('thur_close_time').text.strip()
                if poi.find('fri_open_time').text.strip():
                    hour += " Friday : " + \
                        poi.find('fri_open_time').text.strip() + \
                        poi.find('fri_close_time').text.strip()
                if poi.find('sat_open_time').text.strip():
                    hour += " Saturday : " + \
                        poi.find('sat_open_time').text.strip() + \
                        poi.find('sat_close_time').text.strip()
                if poi.find('sun_open_time').text.strip():
                    hour += " Sunday : " + \
                        poi.find('sun_open_time').text.strip() + \
                        poi.find('sun_close_time').text.strip()

                result_coords.append((lat, lng))
                store = []
    
                store.append(base_url)
                store.append(name if name else "<MISSING>")
                store.append(address if address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zip if zip else "<MISSING>")
                store.append(country if country else "<MISSING>")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hour if hour else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")
                if store[2] in addresses:
                    continue
                addresses.append(store[2])

                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
        except:
            pass

        if current_results_len < MAX_RESULTS:
           # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
