import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('foreyes_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0
    coord = search.next_coord()
    addresses = []
    while coord:
        result_coords = []
        lat = coord[0]
        # logger.info(lat)
        lng = coord[1]
        base_url = "https://www.foreyes.com"
        data = "action=get_properties&lat=39.8283459&lng=-98.5794797&dist=5000&queryType=distance&term=false"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'X-Requested-With': 'XMLHttpRequest',
            'Host': 'www.foreyes.com',
            'Referer': 'https://www.foreyes.com/locations/',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        r = session.get("https://www.foreyes.com/locations?lat="+str(lat)+"&lng="+str(lng),data=data,headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        table = soup.find_all("script")[29]
        data_main = (str(table).split('storeLocations: {"items":')[1].split(',"totalRecords"')[0])
        json_data = json.loads(data_main)
        for store_data in json_data:
            store = []
            store.append("https://www.foreyes.com ")
            store.append(store_data['store_name'])
            store.append(store_data["store_address_line"])
            store.append(store_data['store_city'])
            store.append(store_data['store_state'])
            store.append(store_data["store_zip"])
            store.append("US")
            store.append(store_data['sofe_store_id'])
            store.append(store_data['store_phone'])
            store.append(store_data["store_type"])
            store.append(store_data['store_lat'])
            store.append(store_data["store_long"])
            hours = ""
            if store_data["time_mon_start"] and store_data["time_mon_start"] != "":
                hours = hours + "Monday  " + store_data["time_mon_start"] +" - " + store_data["time_mon_end"] + ", "
            if store_data["time_tue_start"] and store_data["time_tue_start"] != "":
                hours = hours + " tuesday  " + store_data["time_tue_start"] +" - " + store_data["time_tue_end"] + ", "
            if store_data["time_wed_start"] and store_data["time_wed_start"] != "":
                hours = hours + " wednesday  " + store_data["time_wed_start"] +" - " + store_data["time_wed_end"] + ", "
            if store_data["time_thu_start"] and store_data["time_thu_start"] != "":
                hours = hours + " thursday  " + store_data["time_thu_start"] +" - " + store_data["time_thu_end"] + ", "
            if store_data["time_fri_start"] and store_data["time_fri_start"] != "":
                hours = hours + " friday  " + store_data["time_fri_start"] +" - " + store_data["time_fri_end"] + ", "
            if store_data["time_sat_start"] and store_data["time_sat_start"] != "":
                hours = hours + " saturday " + store_data["time_sat_start"] +" - " + store_data["time_sat_end"] + ", "
            if store_data["time_sun_start"] and store_data["time_sun_start"] != "":
                hours = hours + " sunday " + store_data["time_sun_start"] +" - " + store_data["time_sun_end"]
            if hours == "":
                hours = "<MISSING>"
            store.append(hours)
            # store.append(store_data['template_name'])
            store.append("https://www.foreyes.com/locations/"+store_data['url_key'].strip())
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
