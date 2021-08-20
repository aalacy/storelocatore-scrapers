import csv
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
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

    locator_domain = "https://www.mrpuffs.com/"
    page_url = "https://www.mrpuffs.com/en/location/"
    api_url = "https://www.mrpuffs.com/en/location/"
    session = SgRequests()
    r = session.post(api_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="toggle"]')
    for d in div:
        ad = " ".join(d.xpath('.//h4[@class="_h"]/text()'))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = "<MISSING>"
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        latitude = "".join(d.xpath(".//@data-latitude"))
        longitude = "".join(d.xpath(".//@data-longitude"))
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(d.xpath('.//li[./i[@class="fa fa-calendar-check-o"]]/text()'))
            .replace("\n", "")
            .strip()
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
