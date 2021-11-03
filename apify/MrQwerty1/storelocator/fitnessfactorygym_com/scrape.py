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


def get_data(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    hours = tree.xpath(
        ".//p[./strong[contains(text(), 'Hours  of Operation')]]/text()|.//p[./strong[contains(text(), 'STOP')]]/span//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours).replace(":;", ": ") or "<MISSING>"

    iscoming = tree.xpath("//strong[contains(text(), 'Coming Soon')]")
    if iscoming:
        hours_of_operation = "Coming Soon"

    text = "".join(tree.xpath("//iframe/@src"))
    if "embed" in text:
        lat = text.split("!3d")[1].strip().split("!")[0].strip()
        lng = text.split("!2d")[1].strip().split("!")[0].strip()
    else:
        lat = text.split("&lat=")[1].split("&")[0]
        lng = text.split("&long=")[1].split("&")[0]

    return (lat, lng), hours_of_operation


def fetch_data():
    out = []
    locator_domain = "https://www.fitnessfactorygym.com/"
    api_url = "https://www.fitnessfactorygym.com/hours-contact/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-sm-3']")

    for d in divs:
        location_name = "".join(d.xpath("./h2/a/text()")).strip()
        page_url = "".join(d.xpath("./h2/a/@href"))
        coords, hours_of_operation = get_data(page_url)
        line = d.xpath("./div/div/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
            or "<MISSING>"
        )
        latitude, longitude = coords
        location_type = "<MISSING>"

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
