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
    locator_domain = "https://www.adventhealth.com/"
    session = SgRequests()

    for i in range(5000):
        api_url = f"https://www.adventhealth.com/find-a-location?page={i}"
        r = session.get(api_url)
        tree = html.fromstring(r.text)
        li = tree.xpath("//li[@class='facility-search-block__item']")

        for l in li:
            street_address = (
                "".join(l.xpath(".//span[@property='streetAddress']/text()")).strip()
                or "<MISSING>"
            )
            city = (
                "".join(l.xpath(".//span[@property='addressLocality']/text()")).strip()
                or "<MISSING>"
            )
            state = (
                "".join(l.xpath(".//span[@property='addressRegion']/text()")).strip()
                or "<MISSING>"
            )
            postal = (
                "".join(l.xpath(".//span[@property='postalCode']/text()")).strip()
                or "<MISSING>"
            )
            country_code = "US"
            store_number = "<MISSING>"
            slug = "".join(l.xpath(".//h3/a/@href")).strip()
            if slug:
                if slug.startswith("http"):
                    page_url = slug
                else:
                    page_url = f'https://www.adventhealth.com{slug.split("?")[0]}'
                location_name = "".join(l.xpath(".//h3/a/text()")).strip()
            else:
                page_url = "<MISSING>"
                location_name = "".join(l.xpath(".//h3/text()")).strip()
            phone = (
                "".join(l.xpath(".//a[@class='telephone']/text()")).strip()
                or "<MISSING>"
            )
            latitude = (
                "".join(l.xpath(".//a[@property='address']/@data-lat")) or "<MISSING>"
            )
            longitude = (
                "".join(l.xpath(".//a[@property='address']/@data-lng")) or "<MISSING>"
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

        if len(li) < 10:
            break
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
