import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("whistles_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    urls = [
        "https://www.whistles.com/on/demandware.store/Sites-WH-US-Site/en_US/Stores-FindStores?lat=51.378051&long=-3.435973&dwfrm_address_country=US&postalCode=",
        "https://www.whistles.com/on/demandware.store/Sites-WH-UK-Site/en/Stores-FindStores?lat=22.3193039&long=114.1693611&dwfrm_address_country=HK&postalCode=",
        "https://www.whistles.com/on/demandware.store/Sites-WH-UK-Site/en/Stores-FindStores?lat=53.41291&long=-8.24389&dwfrm_address_country=IE&postalCode=",
        "https://www.whistles.com/on/demandware.store/Sites-WH-UK-Site/en/Stores-FindStores?lat=60.12816100000001&long=18.643501&dwfrm_address_country=SE&postalCode=",
        "https://www.whistles.com/on/demandware.store/Sites-WH-UK-Site/en/Stores-FindStores?lat=46.818188&long=8.227511999999999&dwfrm_address_country=CH&postalCode=",
        "https://www.whistles.com/on/demandware.store/Sites-WH-UK-Site/en/Stores-FindStores?lat=37.09024&long=-95.712891&dwfrm_address_country=US&postalCode=",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        website = "whistles.com"
        typ = "<MISSING>"
        logger.info(url)
        for item in json.loads(r.content)["stores"]:
            store = item["ID"]
            name = item["name"]
            add = item["address1"]
            try:
                add = add + " " + item["address2"]
            except:
                pass
            state = "<MISSING>"
            city = item["city"]
            zc = item["postalCode"]
            lat = item["latitude"]
            lng = item["longitude"]
            try:
                phone = item["phone"]
            except:
                phone = "<MISSING>"
            typ = item["storeType"]
            country = item["countryCode"]
            hours = ""
            for day in item["workTimes"]:
                hrs = day["weekDay"] + ": " + day["value"]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            loc = "https://www.whistles.com/us/stores/details?storeID=" + store
            if "Shepton Mallet" in add:
                city = "Shepton Mallet"
                add = add.replace("Shepton Mallet", "").strip()
            if "Kilver Street" in add:
                country = "GB"
            if "Shop 1036" in add:
                zc = "<MISSING>"
            if "Shop 120A" in add:
                city = "Admiralty"
            if city == "":
                city = "<MISSING>"
            yield [
                website,
                loc,
                name,
                add,
                city,
                state,
                zc,
                country,
                store,
                phone,
                typ,
                lat,
                lng,
                hours,
            ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
