from bs4 import BeautifulSoup
import csv
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("godivachocolates_co_uk")


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    # Your scraper here
    data = []
    base_url = "https://www.godivachocolates.co.uk/stores"
    urllist = session.get(base_url, headers=headers, verify=False)
    urllist = BeautifulSoup(urllist.text, "html.parser")

    store_type_list = urllist.find("div", {"class": "shop-types"}).findAll("a")
    for storelink in store_type_list:
        sub_url = base_url + storelink.get("href")
        store_type = storelink.text
        webdata = session.get(sub_url, headers=headers, verify=False)
        webdata = BeautifulSoup(webdata.text, "html.parser")
        store_list = webdata.find(
            "ul", {"class": "pro-stores-list slimscroll-el"}
        ).findAll("a")
        title = "<MISSING>"
        phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours = "<MISSING>"
        postcode = "<MISSING>"
        city = "<FOOL>"

        for stores in store_list:
            store = stores["data-info"]
            store = json.loads(store)
            store_id = store["id"]

            title = store["name"]
            street = store["address"].split("\n")[0]
            city = "<MISSING>"

            if len(store["address"].split("\n")) > 1:
                if len(store["address"].split("\n")[1].split(" ")) > 2:
                    city = " ".join(store["address"].split("\n")[1].split(" ")[2:])
                if len(store["address"].split("\n")) > 2:
                    city = store["address"].split("\n")[2]
                if len(store["address"].split("\n")[1].split(" ")) < 1:
                    city = store["address"].split("\n")[1]
            else:
                city = "<MISSING>"
            if "Email" in city:
                city = "<MISSING>"
            phone = store["phone"]
            if phone == "":
                phone = "<MISSING>"
            latitude = store["latitude"]
            longitude = store["longitude"]
            if latitude == "":
                latitude = "<MISSING>"
            if longitude == "":
                longitude = "<MISSING>"
            postcode = store["postcode"]
            hours = store["working_hours"]
            if postcode == "":
                postcode = " ".join(store["address"].split("\n")[1].split(" ")[0:2])
            data.append(
                [
                    "https://www.godivachocolates.co.uk",
                    sub_url,
                    title,
                    street.rstrip().rstrip(",").strip("\n"),
                    city.rstrip().rstrip(",").strip("\n"),
                    "<MISSING>",
                    postcode,
                    "UK",
                    store_id,
                    phone,
                    store_type,
                    latitude,
                    longitude,
                    hours,
                ]
            )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
