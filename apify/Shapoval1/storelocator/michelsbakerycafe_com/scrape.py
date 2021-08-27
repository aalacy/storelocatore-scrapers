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

    locator_domain = "https://michelsbakerycafe.com"
    api_url = "https://michelsbakerycafe.com/our-boutiques"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "mapMarkers ")]/text()'))
        .split("window.stored.mapMarkers = ")[1]
        .split(";")[0]
    )
    js = json.loads(jsblock)

    for j in js:
        slug = j.get("id")
        page_url = f"https://michelsbakerycafe.com/our-boutiques/#{slug}"
        location_name = j.get("titre")
        location_type = "<MISSING>"
        street_address = j.get("rue")
        state = j.get("province")
        postal = j.get("codepostal")
        country_code = "CA"
        city = j.get("ville")
        store_number = page_url.split("#")[1].strip()
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        phone = (
            "".join(tree.xpath(f'//p[contains(text(), "{street_address}")]/text()[3]'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            "".join(
                tree.xpath(
                    f'//p[contains(text(), "{street_address}")]/preceding::p[@class="item__text mb-0"][1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("TEMPORARILY CLOSURE") != -1:
            hours_of_operation = "Temporarily Closed"
        if hours_of_operation.find("REOPENING") != -1:
            hours_of_operation = hours_of_operation.split("-")[1].strip()

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
