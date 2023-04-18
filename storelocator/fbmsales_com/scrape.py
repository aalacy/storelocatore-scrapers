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
    base_url = "https://www.fbmsales.com"
    res = session.get("https://www.fbmsales.com/locations/")
    soup = bs(res.text, "lxml")
    store_list = soup.select("div.acf-map div.marker")
    data = []
    for store in store_list:
        page_url = store.select_one("a")["href"]

        res1 = session.get(page_url)
        detail = json.loads(
            res1.text.split('<script type="application/ld+json">')[1].split(
                "</script>"
            )[0]
        )

        location_name = store.select_one("a").string
        street_address = detail["@graph"]["address"]["address"]["streetAddress"]
        city = detail["@graph"]["address"]["address"]["addressLocality"]
        state = detail["@graph"]["address"]["address"]["addressRegion"]
        zip = detail["@graph"]["address"]["address"]["postalCode"]
        zip = zip.replace(" ", "") if "-" in zip else zip
        state_zip = state + " " + zip
        street_address = street_address.replace(state_zip, "").strip()
        country_code = detail["@graph"]["address"]["address"]["addressCountry"]
        country_code = country_code or "<MISSING>"
        phone = detail["@graph"]["address"]["address"]["telephone"] or "<MISSING>"
        location_type = detail["@graph"]["@type"]
        store_number = "<MISSING>"
        latitude = store["data-lat"]
        longitude = store["data-lng"]
        hours_of_operation = ", ".join(detail["@graph"]["openingHours"]).strip()
        hours_of_operation = hours_of_operation or "<MISSING>"

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
