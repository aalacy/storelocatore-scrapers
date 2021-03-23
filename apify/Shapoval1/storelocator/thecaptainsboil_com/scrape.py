import csv
import json
from sgscrape.sgpostal import International_Parser, parse_address
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
    locator_domain = "https://thecaptainsboil.com/"
    page_url = "https://thecaptainsboil.com/locations-ca/"
    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = (
        "".join(
            tree.xpath(
                '//script[contains(text(), "var wpgmaps_localize_marker_data")]/text()'
            )
        )
        .split("var wpgmaps_localize_marker_data = ")[1]
        .split("};")[0]
        + "}"
    )
    js = json.loads(block)
    for j in js["6"].values():
        location_name = j.get("title")
        ad = "".join(j.get("address"))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        country_code = "Canada"
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours = "".join(j.get("desc")).replace("\n", "")
        hours = html.fromstring(hours)
        hours_of_operation = " ".join(hours.xpath('//*[contains(text(), ":")]/text()'))
        phone = "".join(hours.xpath('//*[contains(text(), "+")]/text()'))
        postal = "<MISSING>"
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
