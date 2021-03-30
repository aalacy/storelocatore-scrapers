import csv

from sgrequests import SgRequests


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = (
        "https://www.lindtusa.com/wcsstore/storelocator-data/lindt_locations.json"
    )

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    data = []
    locator_domain = "lindtusa.com"

    for store in stores:
        location_name = store["name"]
        street_address = store["address2"].strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["postal"]
        country_code = "US"
        location_type = "<MISSING>"
        phone = store["phone"]
        hours_of_operation = (
            store["hours1"] + " " + store["hours2"] + " " + store["hours3"]
        ).strip()
        latitude = store["lat"]
        longitude = store["lng"]
        store_number = "<MISSING>"
        link = "https://www.lindtusa.com/AjaxStoreLocatorDisplayView?catalogId=13251&langId=-1&storeId=11001"
        if store["web"] and "events" not in store["web"]:
            link = "https://www.lindtusa.com" + store["web"]
            store_number = link.split("-")[-1]

        if state == "Arlington":
            city = state
            state = "VA"

        # Store data
        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
