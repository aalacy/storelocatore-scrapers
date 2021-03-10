import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "PHPSESSID=hq5oifrrj547e1an4c977bb2k1; shoppinglistcookieidentifier=86db87665e311d1b3a32755fac113ae3; __utma=50383083.1320109336.1611237242.1611237242.1611237242.1; __utmc=50383083; __utmz=50383083.1611237242.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; __utmt_aggregate=1; _fbp=fb.1.1611237247298.61575460; __utmb=50383083.6.10.1611237242",
    "Host": "www.shopassociated.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.shopassociated.com"
    r = session.get(base_url + "/locations/?addr=", headers=headers)
    data = r.text.split("var locations = ")[1].split(";")[0]
    data_list = json.loads(data)
    return_main_object = []
    for store_object in data_list:
        store = []

        store.append("https://www.shopassociated.com")
        store.append(base_url + "/locations/?addr=")
        store.append(store_object["name"])
        store.append(store_object["address1"])
        store.append(
            store_object["city"] if store_object["city"] != "" else "<MISSING>"
        )
        store.append(
            store_object["state"] if store_object["state"] != "" else "<MISSING>"
        )
        store.append(
            store_object["zipCode"] if store_object["zipCode"] != "" else "<MISSING>"
        )
        store.append("US")
        store.append(
            store_object["storeNumber"]
            if store_object["storeNumber"] != ""
            else "<MISSING>"
        )
        store.append(
            store_object["phone"] if store_object["phone"] != "" else "<MISSING>"
        )
        store.append(store_object["retailerName"])
        store.append(
            store_object["latitude"] if store_object["latitude"] != "" else "<MISSING>"
        )
        store.append(
            store_object["longitude"]
            if store_object["longitude"] != ""
            else "<MISSING>"
        )
        if "hourInfo" in store_object:
            store.append(
                store_object["hourInfo"].replace("\n", " ")
                if store_object["hourInfo"].replace("\n", ", ") != ""
                else "<MISSING>"
            )
        else:
            store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
