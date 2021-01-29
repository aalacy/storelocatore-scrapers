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
    base_url = "http://www.sneakypetes.com/"

    res = session.get("http://www.sneakypetes.com/locations")
    store_list = json.loads(
        res.text.split("var wpgmaps_localize_marker_data = ")[1].split(";")[0]
    )["2"]
    data = []
    for x in store_list:
        store = store_list[x]
        page_url = store["linkd"]
        location_name = store["title"]
        address = store["address"].split(", ")
        if store["address"][-3:] == "USA":
            address.pop()
        if len(address) == 2:
            state = address[1].split(" ")[1]
            city = address[1].split(" ")[0]
            state_zip = address[1].split(" ").pop()
            address.pop()
        else:
            state_zip = address.pop()
            state = state_zip.split(" ")[0]
            city = address.pop()
        street_address = ", ".join(address)
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>" if store["lat"] == "0" else store["lat"]
        longitude = "<MISSING>" if store["lng"] == "0" else store["lng"]
        res = session.get(page_url)
        soup = bs(res.text, "lxml")
        if location_name == "Verbena Chevron":
            zip = soup.select_one("h1.single-title small").string.split(" ")[:-3].pop()
        else:
            zip = state_zip.split(" ").pop()
        phone = soup.select_one("h1.single-title small").string.split("P: ").pop()
        phone = "<MISSING>" if phone == "" else phone
        hours_of_operation = soup.select_one("div.location-top h3").text
        hours_of_operation = (
            "<MISSING>"
            if "Contact" in hours_of_operation
            else hours_of_operation.replace("Hours of Operations", "").replace("•", "")
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
