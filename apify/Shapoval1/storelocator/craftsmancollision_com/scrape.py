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

    locator_domain = "https://craftsmancollision.com/"
    api_url = "https://craftsmancollision.com/booking-shop-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var jsonShopList = ")]/text()'))
        .split("var jsonShopList = ")[1]
        .split(";")[0]
    )
    js = json.loads(jsblock)
    for j in js:

        page_url = "https://craftsmancollision.com/booking-shop-locator/"
        location_name = j.get("Name")
        location_type = "Craftsman Collision"
        street_address = j.get("Addr1")
        state = j.get("Region")
        postal = j.get("PostalCode")
        country_code = "CA"
        city = j.get("City")
        store_number = "".join(j.get("CompanyId")).replace("C", "").strip()
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        phone = j.get("Phone")
        session = SgRequests()
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[text()="Hours of Operation"]/following-sibling::table[1]//tr/td//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

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
