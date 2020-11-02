import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ramtrucks_com')




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
    zips = sgzip.for_radius(200)
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    for zip_code in zips:
        count = 1
        while True:
            base_url = "https://www.ramtrucks.com"
            r = session.get("https://www.ramtrucks.com/bdlws/MDLSDealerLocator?brandCode=R&func=SALES&radius=200&resultsPage=" +  str(count) + "&resultsPerPage=200&zipCode=" + str(zip_code),headers=headers)
    
            data = r.json()
            if "dealer" not in data:
                break
            data = data["dealer"]
            if data == []:
                break
            for store_data in data:
                if store_data["dealerShowroomCountry"] != "USA":
                    continue
                store = []
                store.append("https://www.ramtrucks.com")
                store.append(store_data["dealerName"])
                store.append(store_data["dealerAddress1"] + " " + store_data["dealerAddress2"])
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(store_data["dealerCity"])
                store.append(store_data["dealerState"])
                store.append(store_data["dealerZipCode"] if len(store_data["dealerZipCode"]) == 5 else store_data["dealerZipCode"][:5] + "-" + store_data["dealerZipCode"][5:])
                store.append("US")
                store.append(str(store_data["dealerCode"]) + "-" + str(store_data["locationSeq"]))
                store.append(store_data["phoneNumber"] if store_data["phoneNumber"] else "<MISSING>")
                if store[-1] != "<MISSING>":
                    # logger.info("https://rw.marchex.io/phone/Ch4NmVi5xREg6wEE/%7B%221%22%3A%22" + str(store[-1].replace(" ","").replace("-","")) + "%22%7D?url=https%3A%2F%2Fwww.ramtrucks.com%2Ffind-dealer.html")
                    phone_request = session.get("https://rw.marchex.io/phone/Ch4NmVi5xREg6wEE/%7B%221%22%3A%22" + str(store[-1].replace(" ","").replace("-","")) + "%22%7D?url=https%3A%2F%2Fwww.ramtrucks.com%2Ffind-dealer.html",headers=headers)
                    if '"ctn"' in phone_request.text:
                        phone = phone_request.text.split('"ctn"')[1].split("}")[0].replace(":","").replace('"','')
                        store[-1] = phone
                store.append("<MISSING>")
                store.append(store_data["dealerShowroomLatitude"])
                store.append(store_data["dealerShowroomLongitude"])
                hours = ""
                for department in store_data["departments"]:
                    hours = hours + " " + department
                    for hour_key in store_data["departments"][department]["hours"]:
                        if store_data["departments"][department]["hours"][hour_key]["closed"] == True:
                            hours = hours + " " + hour_key + " Closed"
                        else:
                            hours = hours + " " + hour_key + " " + store_data["departments"][department]["hours"][hour_key]["open"]["time"] + " " + store_data["departments"][department]["hours"][hour_key]["open"]["ampm"] + " - " + store_data["departments"][department]["hours"][hour_key]["close"]["time"] + " " + store_data["departments"][department]["hours"][hour_key]["close"]["time"]
                store.append(hours if hours else "<MISSING>")
                store.append("<MISSING>")
                yield store
            count = count + 1

def scrape():
    data = fetch_data()
    write_output(data)

scrape()