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
    locator_domain = "https://www.dchauto.com/"
    api_url = "https://www.dchauto.com/car-dealership-locator.htm"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    li = tree.xpath("//li[contains(@class, 'info-window')]")

    for l in li:
        street_address = (
            "".join(l.xpath(".//span[@class='street-address']/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(l.xpath(".//span[@class='locality']/text()")).strip() or "<MISSING>"
        )
        state = (
            "".join(l.xpath(".//span[@class='region']/text()")).strip() or "<MISSING>"
        )
        postal = (
            "".join(l.xpath(".//span[@class='postal-code']/text()")).strip()
            or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "".join(l.xpath(".//a[@class='url']/@href")) or "<MISSING>"
        if page_url.count("http") == 2:
            page_url = page_url.replace("http://", "")
        location_name = (
            "".join(l.xpath(".//span[@class='org']/text()")).strip() or "<MISSING>"
        )
        try:
            phone = l.xpath(".//li[@data-click-to-call]/@data-click-to-call-phone")[
                0
            ].split("?")[0]
        except IndexError:
            phone = "<MISSING>"
        latitude = (
            "".join(l.xpath(".//span[@class='latitude']/text()")).strip() or "<MISSING>"
        )
        longitude = (
            "".join(l.xpath(".//span[@class='longitude']/text()")).strip()
            or "<MISSING>"
        )
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
