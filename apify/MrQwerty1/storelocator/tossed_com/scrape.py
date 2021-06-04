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
    if page_url != r.url:
        return "<MISSING>", "<MISSING>", "<MISSING>"

    latitude = (
        "".join(tree.xpath("//meta[@itemprop='latitude']/@content")) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//meta[@itemprop='longitude']/@content")) or "<MISSING>"
    )
    hours_of_operation = (
        ";".join(tree.xpath("//meta[@itemprop='openingHours']/@content")) or "<MISSING>"
    )
    return latitude, longitude, hours_of_operation


def fetch_data():
    out = []
    locator_domain = "https://www.tossed.com/"
    api = "https://www.tossed.com/locations/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='state-box' and .//a[text()='Visit Website']]")

    for d in divs:
        page_url = "".join(d.xpath(".//a[text()='Visit Website']/@href"))
        location_name = "".join(
            d.xpath(".//p[@class='club-address']/preceding-sibling::text()")
        ).strip()
        state = location_name.split("-")[0].strip()
        city = location_name.split("-")[-1].strip()
        line = d.xpath(".//p[@class='club-address']/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        postal = line[-1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
            or "<MISSING>"
        )
        location_type = "<MISSING>"
        latitude, longitude, hours_of_operation = get_data(page_url)

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
