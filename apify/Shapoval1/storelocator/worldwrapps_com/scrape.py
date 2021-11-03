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

    locator_domain = "https://worldwrapps.com"
    page_url = "https://worldwrapps.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./p/img]")
    for d in div:

        location_name = "".join(d.xpath('.//h3[@class="heading--3"]/text()'))
        location_type = "<MISSING>"
        street_address = (
            "".join(d.xpath('.//p[@class="address"]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(d.xpath('.//p[@class="address"]/text()[3]'))
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(d.xpath('.//span[@class="tel"]/text()'))
            .replace("phone", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        slug = "".join(d.xpath('.//div[@class="new-map"]/@id'))
        latitude = (
            "".join(tree.xpath(f'//script[contains(text(), "{slug}")]/text()'))
            .split(f"{slug}")[1]
            .split("lat:")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath(f'//script[contains(text(), "{slug}")]/text()'))
            .split(f"{slug}")[1]
            .split("lng:")[1]
            .split("}")[0]
            .strip()
        )
        hours_of_operation = (
            "".join(
                d.xpath(
                    './/p[./a[text()="ORDER NOW"]]/following-sibling::p[1]/text()[1]'
                )
            )
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
