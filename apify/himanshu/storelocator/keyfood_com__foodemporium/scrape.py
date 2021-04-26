import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

session = SgRequests()

log = SgLogSetup().get_logger("keyfood.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    page = 0
    while True:
        data = session.get(
            "https://www.keyfood.com/store/keyFood/en/store-locator?q=11756&page="
            + str(page)
            + "&radius=5000000000&all=true",
            headers=headers,
        ).json()["data"]
        for store_data in data:
            store = []
            store.append("https://www.keyfood.com")
            store.append(store_data["displayName"])
            try:
                street = store_data["line1"] + " " + store_data["line2"]
            except:
                store_data["line1"]
            zip_code = store_data["postalCode"]
            if "10305" in street:
                street.replace("10305", "").strip()
                zip_code = "10305"
            store.append(street)
            store.append(store_data["town"])
            store.append(store_data["state"])
            store.append(zip_code)
            store.append("US")
            store.append(store_data["name"])
            store.append(store_data["phone"] if store_data["phone"] else "<MISSING>")

            page_url = store_data["siteUrl"] + store_data["url"].split("?")[0]

            log.info(page_url)

            req = session.get(page_url, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                loc_type = base.find(class_="banner__component simple-banner").img[
                    "title"
                ]
            except:
                loc_type = "<MISSING>"

            store.append(loc_type)
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            try:
                hours = ""
                for hour in store_data["openings"]:
                    hours = hours + " " + hour + " " + store_data["openings"][hour]
            except:
                hours = "<MISSING>"
            store.append(hours.strip() if hours else "<MISSING>")
            store.append(page_url)
            yield store
        if len(data) < 250:
            break
        page = page + 1


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
