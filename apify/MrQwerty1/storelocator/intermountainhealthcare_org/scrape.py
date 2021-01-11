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
    url = "https://intermountainhealthcare.org/"
    session = SgRequests()

    for i in range(1, 5000):
        api_url = (
            f"https://intermountainhealthcare.org/locations/search-results/?page={i}"
        )

        r = session.get(api_url)
        tree = html.fromstring(r.text)
        li = tree.xpath(
            "//li[@class='dir__item dir__item--locations dir__item--grid dir__item--locations']"
        )

        for l in li:
            locator_domain = url
            location_name = "".join(
                l.xpath(".//a[@itemprop='url']/span/text()")
            ).strip()
            slug = "".join(l.xpath(".//a[@itemprop='url']/@href")).strip()
            page_url = f"https://intermountainhealthcare.org{slug}"

            adr1 = "".join(
                l.xpath(".//span[@class='meta-item__street-address1']/text()")
            ).strip()
            adr2 = "".join(
                l.xpath(".//span[@class='meta-item__street-address2']/text()")
            ).strip()

            street_address = f"{adr1} {adr2 or ''}".strip()
            city = (
                "".join(l.xpath(".//span[@itemprop='addressLocality']/text()")).strip()[
                    :-1
                ]
                or "<MISSING>"
            )
            state = (
                "".join(l.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
                or "<MISSING>"
            )
            postal = (
                "".join(l.xpath(".//span[@itemprop='postalCode']/text()")).strip()
                or "<MISSING>"
            )
            country_code = "US"

            store_number = "<MISSING>"
            try:
                phone = l.xpath(".//span[@itemprop='telephone']/text()")[0].strip()
            except IndexError:
                phone = "<MISSING>"
            latitude = (
                "".join(l.xpath(".//meta[@itemprop='latitude']/@content"))
                or "<MISSING>"
            )
            longitude = (
                "".join(l.xpath(".//meta[@itemprop='longitude']/@content"))
                or "<MISSING>"
            )
            if latitude == "0" or longitude == "0":
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            location_type = "<MISSING>"
            hours_of_operation = "<INACCESSIBLE>"

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

        if len(li) < 12:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
