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
    locator_domain = "https://pioneer.bank/"
    page_url = "https://pioneer.bank/About-Pioneer/Locations-Hours/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='place']")

    for d in divs:
        location_name = "".join(d.xpath(".//a/text()")).strip()

        street_address = "".join(
            d.xpath(".//span[@property='streetAddress']/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@property='addressLocality']/text()")).strip()
        state = "".join(d.xpath(".//span[@property='addressRegion']/text()")).strip()
        postal = d.xpath(".//span[@property='postalCode']/text()")[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            d.xpath(".//span[@property='postalCode']/text()")[-1].strip() or "<MISSING>"
        )
        latitude, longitude = "".join(d.xpath("./@data-coords")).split(",")
        location_type = "<MISSING>"
        text = d.xpath("./p/text()")
        hours_of_operation = "<MISSING>"
        for t in text:
            if "Lobby" in t and "at " not in t:
                hours_of_operation = t.replace("Lobby -", "").strip()
                break

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
