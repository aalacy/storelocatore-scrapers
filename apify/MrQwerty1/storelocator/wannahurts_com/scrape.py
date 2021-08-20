import csv
import re

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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://www.wannahurts.com/"
    page_url = "https://www.wannahurts.com/where-it-hurts"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@data-animation-role]")

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='image-slide-title']/text()")
        ).strip()
        source = "".join(d.xpath(".//a[@data-description]/@data-description"))
        root = html.fromstring(source)
        text = "".join(root.xpath(".//a[contains(@href, 'map')]/@href"))
        street_address = "".join(root.xpath("./p[1]/text()")).strip()
        city = location_name.split(",")[0].strip()
        state = location_name.split(",")[1].strip()
        postal = "".join(re.findall(r"\+(\d{5})", text)) or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = "".join(root.xpath("./p/strong/text()")).strip() or "<MISSING>"
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"
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
