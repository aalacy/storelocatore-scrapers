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
    coords = []
    locator_domain = "https://shopcashsaver.com/"
    page_url = "https://shopcashsaver.com/locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//table[@class='locationstable']//td")
    text = "".join(
        tree.xpath("//script[contains(text(), '#map_canvas')]/text()")
    ).split("\n")
    for t in text:
        if not t or "init_googlemaps" in t:
            continue
        lat = t.split("lat: '")[1].split("'")[0]
        lng = t.split("long: '")[1].split("'")[0]
        coords.append((lat, lng))

    for d in divs:
        location_name = "".join(d.xpath(".//h5[@class='storename']/text()")).strip()
        street_address = "".join(
            d.xpath(".//li[contains(@id, 'address')]/text()")
        ).strip()
        line = "".join(d.xpath(".//li[contains(@id, 'citystate')]/text()")).strip()
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = "".join(d.xpath(".//li[contains(@id, 'phone')]/text()")).strip()
        latitude, longitude = coords.pop(0)
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(d.xpath(".//li[contains(@id, 'storehours')]/text()"))
            .replace("Hours:", "")
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
