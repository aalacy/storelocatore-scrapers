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
    base_url = "https://www.gooutdoors.co.uk"
    payload = {
        "postcode": "",
        "submit": "Find stores",
        "radius": "500",
        "ac_store_limit": "300",
        "current_view": "list",
        "fascias[]": "GO",
    }
    r = session.post("https://www.gooutdoors.co.uk/google/store-locator", data=payload)
    soup = bs(r.text, "lxml")
    store_list = soup.select("ul.store-list li")
    data = []
    for store in store_list:
        page_url = (
            base_url
            + store.select("div.store-details div.more_info p")
            .pop()
            .select_one("a")["href"]
        )
        location_name = store.select_one("div.store-details h3 a").string
        res = session.get(page_url)
        detail = json.loads(
            res.text.split('type="application/ld+json">')[1].split("</script>")[0]
        )
        street_address = detail["address"]["streetAddress"]
        country_code = detail["address"]["addressCountry"]
        phone = store.select_one("div.store-details a.tel_link").string
        city = detail["address"]["addressLocality"]
        state = "<MISSING>"
        zip = detail["address"]["postalCode"]
        hours_of_operation = ", ".join(detail["openingHours"])
        geo = res.text.split("maps.LatLng(")[1].split(");")[0]
        latitude = geo.split(", ")[0]
        longitude = geo.split(", ")[1]
        store_number = "<MISSING>"
        location_type = detail["@type"]

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
                '="' + phone + '"',
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
