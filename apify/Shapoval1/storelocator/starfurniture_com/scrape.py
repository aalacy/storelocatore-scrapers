import csv
import json
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []

    locator_domain = "https://www.starfurniture.com"
    page_url = "https://www.starfurniture.com/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath(
        '//div[@class="store-details col col--xs-12 col--sm-6 col--lg-3"]'
    )

    for b in block:
        data = "[" + "".join(b.xpath(".//@data-store")) + "]"
        js = json.loads(data)
        for j in js:
            location_name = "".join(j.get("name"))
            location_type = "<MISSING>"
            street_address = "".join(j.get("address1"))
            if street_address.find("12312") != -1:
                street_address = street_address + " " + j.get("address2")
            phone = j.get("phone")
            state = "TX"
            postal = j.get("postal")
            country_code = j.get("countryCode")
            city = j.get("city")
            store_number = j.get("id")
            latitude = j.get("lat")
            longitude = j.get("lng")
            hours_of_operation = "<MISSING>"
            row = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                postal,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
