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
    base_url = "https://www.flanigans.net"
    res = session.get("https://www.flanigans.net/locations/")
    store_list = json.loads(
        res.text.split('<script type="application/ld+json">')[1].split("</script>")[0]
    )
    data = []
    for store in store_list["subOrganization"]:
        page_url = store["url"]
        res = session.get(page_url)
        soup = bs(res.text, "lxml")
        location_name = store["address"]["name"]
        street_address = store["address"]["streetAddress"].split(",")[0]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip = store["address"]["postalCode"]
        phone = store["telephone"]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = store["@type"]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            soup.select_one("div.loc1")
            .text.split("Online Ordering")
            .pop()
            .split("3793")
            .pop()
            .replace("–", "-")
            .replace("\xa0", " ")
            .replace("’", "'")
            .replace("Open seven days a week", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation[1:]
            if hours_of_operation.startswith(".") or hours_of_operation.startswith(",")
            else hours_of_operation
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
