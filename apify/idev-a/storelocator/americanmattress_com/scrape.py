import csv
import json
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
    base_url = "https://www.americanmattress.com/"
    res = session.get(
        "https://cdn.shopify.com/s/files/1/0027/4474/6102/t/42/assets/sca.storelocatordata.json?v=1610452736&formattedAddress=&boundsNorthEast=&boundsSouthWest="
    )
    store_list = json.loads(res.text)
    data = []

    for store in store_list:
        store_number = store["id"]
        city = store["city"]
        state = store["state"]
        page_url = store["web"] if "web" in store.keys() else "<MISSING>"
        hours_of_operation = (
            store["schedule"]
            .replace("<br>", "")
            .replace("\r", " ")
            .replace("<br>", "")
            .replace("–", "-")
            if "schedule" in store.keys()
            else "<MISSING>"
        )
        location_name = store["name"]
        street_address = store["address"]
        zip = store["postal"]
        country_code = store["country"]
        phone = store["phone"]
        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]
        if hours_of_operation == "<MISSING>" and page_url != "<MISSING>":
            res1 = session.get(page_url)
            soup = bs(res1.text, "lxml")
            try:
                hours_of_operation = (
                    soup.select_one("div.bounceInLeft div.rte")
                    .text.split("Hours")
                    .pop()
                    .replace("\n", " ")
                    .replace("–", "-")
                    .strip()
                )
            except:
                hours_of_operation = "<MISSING>"

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
