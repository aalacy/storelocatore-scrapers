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
    base_url = "https://www.sunrisepreschools.com"
    res = session.get("https://www.sunrisepreschools.com/locations/")
    soup = bs(res.text, "lxml")
    store_list = soup.select("div.mb-sm-5")
    data = []
    for store in store_list:
        page_url = base_url + store.select_one("a")["href"]
        res1 = session.get(page_url)
        detail = json.loads(
            res1.text.split("<script type='application/ld+json'>")[1].split(
                "</script>"
            )[0]
        )
        location_name = detail["name"].replace("&amp;", "")
        street_address = detail["address"]["streetAddress"]
        city = detail["address"]["addressLocality"]
        state = detail["address"]["addressRegion"]
        zip = detail["address"]["postalCode"]
        country_code = detail["address"]["addressCountry"] or "<MISSING>"
        phone = detail["address"]["telephone"] or "<MISSING>"
        location_type = detail["@type"]
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            bs(res1.text, "lxml")
            .select_one("dl.row")
            .text.split("Hours:\n")[1]
            .split("\n")[0]
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
