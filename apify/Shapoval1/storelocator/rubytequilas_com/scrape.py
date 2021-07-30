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

    locator_domain = "http://rubytequilas.com"
    page_url = "http://rubytequilas.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(
            tree.xpath(
                '//script[contains(text(), "wpgmaps_localize_marker_data ")]/text()'
            )
        )
        .split("wpgmaps_localize_marker_data = ")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(jsblock)
    js = js["1"]
    for j in js.values():

        location_name = j.get("title")
        location_type = "<MISSING>"
        ad = j.get("address")
        ad = html.fromstring(ad)
        street_address = "".join(ad.xpath("//text()[1]"))
        adr = "".join(ad.xpath("//text()[2]")).strip()
        state = adr.split(",")[1].split()[0].strip()
        postal = adr.split(",")[1].split()[1].strip()
        country_code = "USA"
        city = adr.split(",")[0].strip()
        store_number = j.get("marker_id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        desc = j.get("desc")
        desc = html.fromstring(desc)
        phone = (
            "".join(desc.xpath("//text()")).split("\n")[0].replace("RUBY ", "").strip()
        )
        hours_of_operation = (
            " ".join(desc.xpath("//text()")[2:4]).replace("\n", "").strip()
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
