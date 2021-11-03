import csv

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
    locator_domain = "https://seipdrug.com/"
    page_url = "https://seipdrug.com/stores/locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'dataRaw')]/text()"))
    text = (
        text.split('dataRaw: "')[1]
        .split('",')[0]
        .replace("\\n", "")
        .replace("\\t", " ")
        .replace("\\", "")
        .replace('<?xml version="1.0" encoding="utf-8"?>', "")
    )
    root = html.fromstring(text)
    divs = root.xpath("//marker")

    for d in divs:
        location_name = "".join(d.xpath("./@name"))
        adr = "".join(d.xpath("./@address"))
        adr2 = "".join(d.xpath("./@address2")) or ""
        street_address = f"{adr} {adr2}".strip()
        city = "".join(d.xpath("./@city")) or "<MISSING>"
        state = "".join(d.xpath("./@state")) or "<MISSING>"
        postal = "".join(d.xpath("./@postal")) or "<MISSING>"
        country_code = "".join(d.xpath("./@country")) or "<MISSING>"
        store_number = "<MISSING>"
        phone = "".join(d.xpath("./@phone")) or "<MISSING>"
        latitude = "".join(d.xpath("./@lat")) or "<MISSING>"
        longitude = "".join(d.xpath("./@lng")) or "<MISSING>"
        location_type = "".join(d.xpath("./@category")) or "<MISSING>"

        _tmp = []
        for i in range(1, 8):
            line = "".join(d.xpath(f"./@hours{i}"))
            if not line:
                break
            _tmp.append(line)

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
