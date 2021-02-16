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
    locator_domain = "https://www.rag-bone.com/"
    api_url = "https://www.rag-bone.com/stores"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='sl-store clearfix sl__store']")

    for d in divs:
        slug = "".join(d.xpath(".//a[@class='sl__store-details-name']/@href"))
        page_url = f"https://www.rag-bone.com{slug}"
        street_address = (
            "".join(d.xpath(".//div[@itemprop='streetAddress']/text()")).strip()
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

        phone = (
            "".join(d.xpath(".//span[@itemprop='telephone']/text()")).strip()
            or "<MISSING>"
        )

        if len(postal) == 5:
            country_code = "US"
        elif phone.startswith("+44"):
            country_code = "GB"
        else:
            continue

        store_number = "<MISSING>"
        location_name = "".join(
            d.xpath(".//a[@class='sl__store-details-name']/text()")
        ).strip()

        text = "".join(d.xpath(".//*[@data-pin]/@data-pin"))
        try:
            lat_lon = eval(text)
            latitude, longitude = lat_lon[1:3]
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"

        hours = d.xpath(
            ".//div[@class='sl__store-details-hours sl__store-details-txt']/text()"
        )
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
