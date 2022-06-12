import csv
import json
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
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

    locator_domain = "https://lonestartexasgrill.com"

    page_url = "https://lonestartexasgrill.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    div = (
        "".join(tree.xpath('//script[contains(text(), "var geoData")]/text()'))
        .split("var geoData            = ")[1]
        .split("}]},")[0]
        + "}]}"
    )
    div = div.replace('{"type":"FeatureCollection","features":', "").replace(
        "}]}", "}]"
    )
    js = json.loads(div)

    for j in js:

        ad = j.get("properties")
        adr = "".join(ad.get("address"))
        if adr.find("(") != -1:
            adr = adr.split("(")[0].strip()
        location_name = ad.get("name")
        slug = "".join(ad.get("uniqId"))
        page_url = f"https://lonestartexasgrill.com/locations/{slug}"
        location_type = "<MISSING>"
        a = parse_address(International_Parser(), adr)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        phone = ad.get("phone")
        country_code = "CA"
        store_number = "<MISSING>"
        latitude = j.get("geometry").get("coordinates")[1]
        longitude = j.get("geometry").get("coordinates")[0]
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath('//ul[@class="location-details-hours"]/li/span/text()'))
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
