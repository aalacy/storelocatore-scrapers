import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import  datetime
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('dollargeneral_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 250
    MAX_DISTANCE = 50
    current_results_len = 0    
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    

    while zip_code:
        result_coords = []

        # logger.info("zip_code === "+zip_code)
        data = '{"request":{"appkey":"9E9DE426-8151-11E4-AEAC-765055A65BB0","formdata":{"geoip":false,"dataview":"store_default","geolocs":{"geoloc":[{"addressline":"'+str(zip_code)+'","country":"US","latitude":"","longitude":""}]},"searchradius":"10|20|50|100","where":{"nci":{"eq":""},"and":{"PROPANE":{"eq":""},"REDBOX":{"eq":""},"RUGDR":{"eq":""},"MULTICULTURAL_HAIR":{"eq":""},"TYPE_ID":{"eq":""},"DGGOCHECKOUT":{"eq":""},"FEDEX":{"eq":""},"DGGOCART":{"eq":""}}},"false":"0"}}}'
        
        
        location_url = "http://hosted.where2getit.com/dollargeneral/rest/locatorsearch?like=0.9394142712975708"
        # http://hosted.where2getit.com/dollargeneral/rest/locatorsearch?like=0.06990333019617112&lang=en_US
        try:

            loc = session.post(location_url,headers=headers,data=data).json()
        except:
            pass
      

        locator_domain = "https://www.dollargeneral.com/"
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        hours_of_operation = ""

        hours_of_operation =''
       
        if "collection" in loc['response']:
            current_results_len = len(loc['response']['collection']) 
            for data in loc['response']['collection']:
                store_number = data['name'].split("#")[-1]
                try:
                    hours_of_operation =' Monday '+ str(datetime.strptime(data['opening_time_mon'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p"))+ ' - ' + \
                    str(datetime.strptime(data['closing_time_mon'].replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p"))+","+' Tuesday ' +str(datetime.strptime(data['opening_time_tue'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p"))\
                    + ' - ' +str(datetime.strptime(data['closing_time_tue'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p")) +","+ ' Wednesday ' + str(datetime.strptime(data['opening_time_wed'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p")) \
                    + ' - ' +str(datetime.strptime(data['closing_time_wed'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p")) +","+ ' Thursday ' + str(datetime.strptime(data['opening_time_thu'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p")) \
                    + ' - ' +str(datetime.strptime(data['closing_time_thu'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p"))+","+ ' Friday ' + str(datetime.strptime(data['opening_time_fri'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p")) \
                    + ' - ' +str(datetime.strptime(data['closing_time_fri'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p"))+","+ ' Saturday ' + str(datetime.strptime(data['opening_time_sat'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p")) \
                    + ' - ' +str(datetime.strptime(data['closing_time_sat'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p"))+","+ ' Sunday ' + str(datetime.strptime(data['opening_time_sun'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p")) \
                    + ' - ' +str(datetime.strptime(data['closing_time_sun'].replace("7.:00","07:00").replace("8.:00","08:00").replace("24:00","00:00"), "%H:%M").strftime("%I:%M %p"))
                except:
                    hours_of_operation = "<MISSING>"

                
                p = store_number.strip()
                page_url = "http://www2.dollargeneral.com/Savings/Circulars/Pages/index.aspx?store_code="+str(p)
                result_coords.append((latitude, longitude))
                store = [locator_domain, data['name'], data['address1'], data['city'], data['state'], data['postalcode'], country_code,
                        store_number, data['phone'], location_type, data['latitude'], data['longitude'], hours_of_operation,page_url]

                if store[2] + store[-3] in addresses:
                    continue

                addresses.append(store[2] + store[-3])
                store = [x.strip() if x else "<MISSING>" for x in store]

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                yield store
          

       
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
