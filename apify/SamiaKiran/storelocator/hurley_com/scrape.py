import csv
import json
from sgrequests import SgRequests
from sglogging import sglog

website = "hurley_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    data = []
    url = "https://stockist.co/api/v1/u5986/locations/all.js?callback=_stockistAllStoresCallback"
    r = session.get(url, headers=headers)
    loclist = r.text.split("_stockistAllStoresCallback(")[1].split(");", 1)[0]
    loclist = json.loads(loclist)
    for loc in loclist:
        title = loc["name"]
        store = loc["id"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        title = loc["name"]
        phone = loc["phone"]
        temp = loc["address_line_2"]
        if temp is None:
            street = loc["address_line_1"]
        else:
            street = loc["address_line_1"]
            street = street + " " + temp
        city = loc["city"]
        state = loc["state"]
        pcode = loc["postal_code"]
        ccode = loc["country"]
        data.append(
            [
                "https://www.hurley.com/",
                "https://www.hurley.com/pages/store-locator",
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                "<MISSING>",
            ]
        )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()
