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

    locator_domain = "https://www.beautycounter.com"
    api_url = "https://www.beautycounter.com/store-locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(
        tree.xpath('//script[contains(text(), "callToActionUrl")]/text()')
    ).split('callToActionUrl":"')
    slugs = []
    for a in div:
        slug = a.split('"')[0]
        slugs.append(slug)

    for d in slugs:

        page_url = f"{locator_domain}{d}".replace("u002F", "").replace("\\", "/")
        if page_url.find("STATE") != -1:
            continue
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        jsblock = (
            "".join(tree.xpath('//script[contains(text(), "textLocation")]/text()'))
            .split('"fields":{"textLocation"')[1]
            .split("}")[0]
        )
        jsblock = '{"textLocation"' + jsblock + "}"
        js = json.loads(jsblock)
        location_name = js.get("title")
        location_type = "<MISSING>"
        ad = (
            "".join(js.get("textLocation"))
            .replace("Blvd,", "Blvd")
            .replace("New York", "New_York")
            .replace("Wharf,", "Wharf")
        )
        street_address = " ".join(ad.split(",")[0].split()[:-1])
        phone = js.get("textPhoneNumber")
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].split()[-1].replace("_", " ").strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            "".join(js.get("body"))
            .split("__Store Hours:__")[1]
            .replace("\n", "")
            .replace("<br>", "")
            .split("Now")[0]
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
