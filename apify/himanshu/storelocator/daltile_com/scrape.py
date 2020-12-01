import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    MAX_RESULTS = 1000
    MAX_DISTANCE = 150
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    current_results_len = 0
    adressess = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }

    base_url = "https://www.daltile.com"

    while zip_code:
        result_coords =[]
        
        r = session.post("https://hosted.where2getit.com/daltile/rest/locatorsearch",
                          headers=headers,
                          data='{"request":{"appkey":"085E99FA-1901-11E4-966B-82C955A65BB0","formdata":{'
                               '"dynamicSearch":true,"geoip":false,"dataview":"store_default","limit":1000,'
                               '"geolocs":{"geoloc":[{"addressline":"' + str(zip_code) + '","country":"","latitude":"",'
                                                                                         '"longitude":""}]},"searchradius":"1000"}}}')

        # key = {"request":{"appkey":"085E99FA-1901-11E4-966B-82C955A65BB0","formdata":{"dynamicSearch":true,"geoip":false,"dataview":"store_default","limit":250,"order":"PREMIERSTATEMENTSDEALER asc, SHOWROOM asc, LOCATION_RATING::numeric desc nulls last, _distance","geolocs":{"geoloc":[{"addressline":"99503","country":"","latitude":"","longitude":""}]},"searchradius":"250","stateonly":"1","where":{"clientkey":{"distinctfrom":"12345"},"locator":{"eq":"1"},"badge":{"distinctfrom":"Not On Locator"},"daltile":{"eq":"1"},"or":{"showroom":{"eq":"1"},"premierstatementsdealer":{"eq":"1"},"authorizeddealer":{"eq":"1"},"daltileservicecenter":{"eq":"1"},"tile_mosaics":{"eq":""},"stone_slab_countertops":{"eq":"1"}}},"true":"1","false":"0"}}}
        
        json_data = r.json()
        locator_domain = base_url
        location_name = ""
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zipp = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = "daltile"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        raw_address = ""
        hours_of_operation = "<MISSING>"
        page_url = "<MISSING>"
        if 'collection' in json_data['response']:
    
            for address_list in json_data['response']['collection']:
                current_results_len = len(json_data['response']['collection'])
                latitude = address_list['latitude']
                longitude = address_list['longitude']
                zipp = address_list['postalcode']
                location_name = address_list['name']
                city = address_list['city']
                country_code = address_list['country']
                location_type = address_list['storetype']
                state = address_list['state']
                street_address = address_list['address1']
                phone = address_list['phone']
                if street_address is not None:
                    if address_list['address2'] is not None:
                        street_address += ", " + address_list['address2']
                    soup_street_address = BeautifulSoup(street_address, "lxml")
                    street_address = ", ".join(list(soup_street_address.stripped_strings))
                else:
                    street_address = '<MISSING>'

                if location_name is None or len(location_name) == 0:
                    location_name = "<MISSING>"

                if street_address is None or len(street_address) == 0:
                    street_address = "<MISSING>"

                if city is None or len(city) == 0:
                    city = "<MISSING>"

                if state is None or len(state) == 0:
                    state = "<MISSING>"

                if zipp is None or len(zipp) == 0:
                    zipp = "<MISSING>"
                else:
                    if not any(char.isdigit() for char in zipp):
                       
                        zipp = "<MISSING>"

                # if country_code is None or len(country_code) == 0:
                if latitude is None or len(latitude) == 0:
                    latitude = "<MISSING>"

                if longitude is None or len(longitude) == 0:
                    longitude = "<MISSING>"

                if phone is None or len(phone) == 0:
                    phone = "<MISSING>"

                is_missing_hours = True
                if address_list['sunday_open'] is not None and address_list['sunday_closed'] is not None:
                    is_missing_hours = False
                    hours_of_operation = "Sunday = " + address_list['sunday_open'] + " - " + address_list['sunday_closed'] + ", "
                else:
                    hours_of_operation += "Sunday = CLOSED" + ", "

                if address_list['monday_open'] is not None and address_list['monday_closed'] is not None:
                    is_missing_hours = False
                    hours_of_operation += "Monday = " + address_list['monday_open'] + " - " + address_list['monday_closed'] + ", "
                else:
                    hours_of_operation += "Monday = CLOSED" + ", "

                if address_list['tuesday_open'] is not None and address_list['tuesday_closed'] is not None:
                    is_missing_hours = False
                    hours_of_operation += "Tuesday = " + address_list['tuesday_open'] + " - " + address_list[
                        'tuesday_closed'] + ", "
                else:
                    hours_of_operation += "Tuesday = CLOSED" + ", "

                if address_list['wednesday_open'] is not None and address_list['wednesday_closed'] is not None:
                    is_missing_hours = False
                    hours_of_operation += "Wednesday = " + address_list['wednesday_open'] + " - " + address_list[
                        'wednesday_closed'] + ", "
                else:
                    hours_of_operation += "Wednesday = CLOSED" + ", "

                if address_list['thursday_open'] is not None and address_list['thursday_closed'] is not None:
                    is_missing_hours = False
                    hours_of_operation += "Thursday = " + address_list['thursday_open'] + " - " + address_list[
                        'thursday_closed'] + ", "
                else:
                    hours_of_operation += "Thursday = CLOSED" + ", "

                if (address_list['friday_open'] is not None) and (address_list['friday_closed'] is not None):
                    is_missing_hours = False
                    hours_of_operation += "Friday = " + address_list['friday_open'] + " - " + address_list[
                        'friday_closed'] + ", "
                else:
                    hours_of_operation += "Friday = CLOSED" + ", "

                if (address_list['saturday_open'] is not None) and (address_list['saturday_closed'] is not None):
                    is_missing_hours = False
                    hours_of_operation += "Saturday = " + address_list['saturday_open'] + " - " + address_list[
                        'saturday_closed']
                else:
                    hours_of_operation += "Saturday = CLOSED"

                hours_of_operation = hours_of_operation.replace('CLOSED - CLOSED', 'CLOSED')

                if is_missing_hours:
                    hours_of_operation = "<MISSING>"
                result_coords.append((latitude, longitude))
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(country_code)
                store.append("<MISSING>")
                store.append(phone)
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append("<MISSING>")
                if store[2] in adressess:
                    continue
                adressess.append(store[2])
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store
        else:
            pass


        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
        
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)
scrape()

