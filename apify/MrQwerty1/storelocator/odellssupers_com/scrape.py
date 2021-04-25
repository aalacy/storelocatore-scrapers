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
    locator_domain = "https://odellssupers.com/"
    page_url = locator_domain

    session = SgRequests()
    r = session.get(locator_domain)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='location-data']")

    for d in divs:
        street_address = (
            " ".join(
                d.xpath(".//div[contains(@class, 'site-loc-address')]/text()")
            ).strip()
            or "<MISSING>"
        )
        csz = "".join(d.xpath(".//div[@class='site-city-state-zip']/text()")).strip()
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[1].strip()
        state = csz.split()[0]
        postal = csz.split()[1]
        country_code = "US"
        store_number = "".join(d.xpath("./@data-location-id")) or "<MISSING>"
        location_name = "".join(d.xpath(".//a[@class='title_color']/text()")).strip()
        phone = (
            "".join(d.xpath(".//div[@class='site-loc-phone']/text()"))
            .replace("Phone:", "")
            .strip()
            or "<MISSING>"
        )
        latitude = "".join(d.xpath("./@data-lat")) or "<MISSING>"
        longitude = "".join(d.xpath("./@data-lon")) or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(d.xpath(".//div[@class='site-loc-hours']/text()"))
            .replace("Hours:", "")
            .strip()
            .replace("PM ", "PM; ")
            or "<MISSING>"
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
