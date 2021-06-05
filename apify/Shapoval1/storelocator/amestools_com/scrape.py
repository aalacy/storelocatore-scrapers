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
    locator_domain = "https://amestools.com"
    page_url = "https://amestools.com/store-locator/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    block = (
        "".join(tree.xpath('//script[@id="maplistko-js-extra"]/text()'))
        .split("var maplistScriptParamsKo = ")[1]
        .split("/*")[0]
        .replace("};", "}")
    )
    js = json.loads(block)
    for j in js["KOObject"][0]["locations"]:
        location_name = j.get("title")
        ad = j.get("address")
        ad = html.fromstring(ad)
        line = ad.xpath("//*//text()")
        line = list(filter(None, [a.strip() for a in line]))
        line = " ".join(line)
        if line.find("Phone:") != -1:
            line = line.split("Phone:")[0].strip()
        a = parse_address(International_Parser(), line)

        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        country_code = "US"
        if state == "AB" or state == "BC" or state == "MB" or state == "ON":
            country_code = "CA"
        postal = a.postcode or "<MISSING>"
        store_number = "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = "<MISSING>"
        hours = j.get("description")
        hours = html.fromstring(hours)
        hoo = " ".join(hours.xpath("//*//text()")).replace("\n", "").strip()
        phone = hoo.split("Phone:")[1].strip()
        if phone.find("Email") != -1:
            phone = hoo.split("Email")[0].strip()
        if phone.find("Fax") != -1:
            phone = hoo.split("Fax")[0].strip()
        hours_of_operation = "<MISSING>"
        if hoo.find("Store Hours:") != -1:
            hours_of_operation = hoo.split("Store Hours:")[1]
        if phone.find("Phone:") != -1:
            phone = phone.split("Phone:")[1].strip()

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
