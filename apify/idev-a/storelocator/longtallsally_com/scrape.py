import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

session = SgRequests()


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
    base_url = "https://www.longtallsally.com"
    res = session.get(
        "https://www.longtallsally.com/store-finder",
    )
    store_list = bs(res.text, "lxml").select(
        "div#GreatBritainNorthernIreland div.card--flat"
    )
    data = []

    for store in store_list:
        location_name = store.select_one("a h5").string
        page_url = base_url + store.select("a").pop()["href"]
        city = "<MISSING>"
        state = "<MISSING>"
        street_address = (
            store.select_one("span.storeSingleLine").string.replace("\r\n", " ").strip()
        )
        street_address = (
            street_address[:-1] if street_address.endswith(",") else street_address
        )
        zip = store.select_one("span.storePostcode").string
        country_code = "GB"
        phone = store.select_one("a.storeTelephone").string
        store_number = "<MISSING>"
        location_type = store["data-storetype"]
        latitude = store["data-latitude"]
        longitude = store["data-longitude"]
        hours = store.select_one("span.storeOpening").contents[2:]
        hours = [x.strip() for x in hours if x.string is not None]
        hours = [x for x in hours if x]
        hours_of_operation = " ".join(hours) or "<MISSING>"
        hours_of_operation = hours_of_operation.replace(
            "Currently closed due to Government measures", "(Temporarily closed)"
        )

        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
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


if __name__ == "__main__":
    scrape()
