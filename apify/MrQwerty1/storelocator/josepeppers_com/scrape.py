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


def get_hours(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    hours = tree.xpath("//p[./i[@class='fa fa-clock-o']]/following-sibling::p/text()")
    hours = list(filter(None, [h.strip() for h in hours]))

    return ";".join(hours) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://www.josepeppers.com/"
    api_url = "https://www.josepeppers.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-xs-12 col-sm-6 col-location']")

    for d in divs:
        street_address = (
            "".join(d.xpath(".//span[@itemprop='streetAddress']/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
            or "<MISSING>"
        )
        state = (
            "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
            or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        slug = "".join(d.xpath(".//a[@class='find-location']/@href"))
        page_url = f"https://www.josepeppers.com{slug}"
        location_name = (
            "".join(d.xpath(".//span[@itemprop='name']/text()")).strip() or "<MISSING>"
        )
        phone = (
            "".join(d.xpath(".//span[@itemprop='telephone']/text()")).strip()
            or "<MISSING>"
        )
        latitude = (
            "".join(d.xpath(".//meta[@itemprop='latitude']/@content")) or "<MISSING>"
        )
        longitude = (
            "".join(d.xpath(".//meta[@itemprop='longitude']/@content")).strip()
            or "<MISSING>"
        )
        location_type = "<MISSING>"
        hours_of_operation = get_hours(page_url)

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
