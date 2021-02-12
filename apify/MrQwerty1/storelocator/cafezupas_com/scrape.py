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
    locator_domain = "https://cafezupas.com/"
    api_url = "https://cafezupas.com/locations.html"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class,'grid-item')]")

    for d in divs:
        line = d.xpath(
            ".//p[@class='text-small text-extra-dark-gray margin-5px-top']/text()"
        )
        if not line:
            continue
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        try:
            postal = line.split()[1]
        except IndexError:
            postal = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "https://cafezupas.com/locations.html"
        location_name = "".join(
            d.xpath(".//a[contains(@class,'popup-youtube post-title')]/text()")
        ).strip()
        phone = (
            " ".join(
                "".join(d.xpath(".//a[contains(@href,'tel')]/text()")).split()
            ).replace("Layton ", "")
            or "<MISSING>"
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(
                "".join(
                    d.xpath(".//p[@class='text-small text-extra-dark-gray']/text()")
                )
                .strip()
                .replace("\n", ";")
                .split()
            )
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
