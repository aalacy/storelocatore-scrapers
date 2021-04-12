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
    locator_domain = "https://spencediamonds.com/"
    page_url = "https://spencediamonds.com/visit-us/spence-locations/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class, 'standard_section  locations')]")

    for d in divs:
        location_name = "".join(d.xpath(".//h5/text()")).strip()
        street_address = "".join(
            d.xpath(".//p[./a[contains(text(), 'Click')]]/text()")
        ).strip()
        city = location_name.split(",")[0].strip()
        state = location_name.split(",")[1].strip()
        postal = "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        phone = "".join(d.xpath(".//h4/a/text()")) or "<MISSING>"
        text = "".join(d.xpath(".//a[contains(@href, 'maps')]/@href"))
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"

        hours = d.xpath(".//strong[text()='Store Hours']/following-sibling::text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours) or "<MISSING>"

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
