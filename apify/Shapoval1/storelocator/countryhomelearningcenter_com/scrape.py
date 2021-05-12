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

    locator_domain = "https://countryhomelearningcenter.com"
    page_url = "https://countryhomelearningcenter.com/contact/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    block1 = (
        "".join(tree.xpath('//script[contains(text(), "7611 W Loop")]/text()'))
        .split("addresses: ")[1]
        .split("],")[0]
        + ","
    )
    block2 = (
        "".join(tree.xpath('//script[contains(text(), "13120 US-183")]/text()'))
        .split("addresses: [")[1]
        .split("],")[0]
        + "]"
    )
    block = block1 + block2
    js = json.loads(block)
    for j in js:

        location_type = "<MISSING>"
        ad = "".join(j.get("address"))
        ad = html.fromstring(ad)
        ad = ad.xpath("//*/text()")
        if len(ad) == 5:
            ad = list(ad)
            del ad[0]

        street_address = "".join(ad[1]).replace("\n", "").replace(",", "").strip()
        phone = "".join(ad[3]).replace("\n", "").strip()
        adr = "".join(ad[2]).replace("\n", "").strip()

        city = adr.split(",")[0].strip()
        state = adr.split(",")[1].split()[0].strip()
        postal = adr.split(",")[1].split()[-1].strip()

        country_code = "US"
        location_name = "".join(ad[0]).replace("\n", "").replace(",", "").strip()
        store_number = "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
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
