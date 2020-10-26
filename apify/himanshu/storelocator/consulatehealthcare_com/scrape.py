import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from datetime import datetime
session = SgRequests()
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('consulatehealthcare_com')



def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://momentfeed-prod.apigee.net/api/v2/llp/sitemap?auth_token=YNDRAXWGIEKBMEAP&country=US&multi_account=false"
    addressess=[]
    # for q in range(0,1000):
    # querystring = {"auth_token":"YNDRAXWGIEKBMEAP","center":"41.2524,-95.998","coordinates":"-9.96885060854611,-40.60546875,70.4367988185464,-151.34765625","multi_account":"false","page":str(q),"pageSize":"1000"}
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        'accept': "application/json, text/plain, */*",
        'cache-control': "no-cache",
        "Authorization": "YNDRAXWGIEKBMEAP",

        }

    response = session.get(url, headers=headers).json()
    for data in response['locations']: 
        logger.info(data)
        # exit()
        locator_domain='http://consulatehealthcare.com/'
        street_address = data['store_info']['address']
        street_address1 = data['store_info']['address_extended']
        page_url = "https://centers.consulatehealthcare.com"+data['llp_url']
        # logger.info("page",page_url)
        city = data['store_info']['locality']
        zipp = data['store_info']['postcode']
        state = data['store_info']['region']
        api="https://momentfeed-prod.apigee.net/api/llp.json?address="+page_url.split("/")[-1].replace("-",'+').replace("_",'.')+"&locality="+city.replace(" ","+")+"&multi_account=false&pageSize=30&region="+str(state)
        response1 = session.get(api, headers=headers).json()
        for data1 in response1:
            location_name = data1['store_info']['name']
            # logger.info(data1['store_info']
            phone = data1['store_info']['phone']
            latitude =data1['store_info']['latitude']
            longitude = data1['store_info']['longitude']
            store_number = '<MISSING>'
        country_code = "US"
        hours_of_operation = '<MISSING>'
        # hours = data['store_info']['hours']

    #     day = {'1':'Monday','2':'Tuesday','3':'Wednesday','4':'Thursday','5':'Friday','6':'Saturday','7':'Sunday'}

    #     hour = data['store_info']['hours']
    #     hours = ''
        location_type= "<MISSING>"
    #     for i in hour.split(";")[:-1]:
    #         start_time = datetime.strptime(i.split(",")[1],"%H%M").strftime("%I:%M %p")
    #         end_time = datetime.strptime(i.split(",")[2],"%H%M").strftime("%I:%M %p")
    #         hours+= day[str(i.split(",")[0])] +" "+ str(start_time)+" to "+ str(end_time) + " "        
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        # logger.info("store--------------------",store)
        yield store



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
