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
    locator_domain = "https://www.galaxytheatres.com"
    api_url = "https://www.galaxytheatres.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='locations__item box box--nested hasMap']")

    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        line = d.xpath(
            ".//span[@class='locations__addressCol locations__text']/span/text()"
        )
        street_address = line[0]
        city = line[1]
        state = line[2]
        postal = line[3]
        country_code = "US"
        store_number = "<MISSING>"
        slug = "".join(
            d.xpath(".//a[@class='button button--secondary']/@href")
        ).replace("/contact", "")
        page_url = f"{locator_domain}{slug}"
        phone = (
            "".join(
                d.xpath(
                    ".//span[@class='locations__text icon icon--before icon--phone']/a/text()"
                )
            ).strip()
            or "<MISSING>"
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
