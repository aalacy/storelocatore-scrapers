import csv
import requests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('trekbikes_com')



def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.trekbikes.com"
    r = requests.get("https://www.trekbikes.com/us/en_US/store-finder/json/?q=11756&sort=Distance&distance=100000",headers=headers)
    page_size = r.json()["searchPageData"]["pagination"]["numberOfPages"]
    return_main_object = []
    for i in range(page_size):
        while True:
           # logger.info("https://www.trekbikes.com/us/en_US/store-finder/json/?q=11756&sort=Distance&distance=100000&page="+str(i))
            page_request = requests.get("https://www.trekbikes.com/us/en_US/store-finder/json/?q=11756&sort=Distance&distance=100000&page="+str(i),headers=headers)
            try:
                location_list = page_request.json()["searchPageData"]["results"]
                for store_data in location_list:
                    address = ""
                    if "line1" in store_data["address"] and store_data["address"]["line1"] != None:
                        address = address + store_data["address"]["line1"]
                    if "line2" in store_data["address"] and store_data["address"]["line2"] != None:
                        address = address + store_data["address"]["line2"]
                    store = []
                    store.append("https://www.trekbikes.com")
                    store.append(store_data["displayName"])
                    store.append(address)
                    store.append(store_data["address"]["town"])
                    if store_data["address"]["region"] != None:
                        store.append(store_data["address"]["region"]["isocodeShort"])
                    else:
                        store.append("<MISSING>")
                    store.append(store_data["address"]["postalCode"] if store_data["address"]["postalCode"] != "" and store_data["address"]["postalCode"] != None else "<MISSING>")
                    if "country" not in store_data["address"]:
                        store.append(store_data["address"]["region"]["countryIso"])
                    else:
                        store.append(store_data["address"]["country"]["isocode"])
                    if store[-1] != "CA" and store[-1] != "US":
                        continue
                    store.append(store_data["name"])
                    store.append(store_data["address"]["phone"].split("/")[0].split("or")[0].replace("RIDE","").split(",")[0] if store_data["address"]["phone"] != "" and store_data["address"]["phone"] != None else "<MISSING>")
                    store.append("trek")
                    store.append(store_data["geoPoint"]["latitude"])
                    store.append(store_data["geoPoint"]["longitude"])
                    hours = ""
                    if store_data["openingHours"] == None:
                        hours = ""
                    else:
                        store_hours = store_data["openingHours"]["weekDayOpeningList"]
                        for i in range(len(store_hours)):
                            if store_hours[i]["storeOpeningTime"] == None:
                                hours = hours + " " + store_hours[i]["weekDay"] + " Closed "
                            else:
                                hours = hours + " " + store_hours[i]["weekDayLong"] + " " + store_hours[i]["storeOpeningTime"]["formattedHour"] + " - " + store_hours[i]["storeClosingTime"]["formattedHour"]
                    store.append(hours if hours != "" else "<MISSING>")
                    # return_main_object.append(store)
                    yield store
                break
            except:
                continue
    # return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
