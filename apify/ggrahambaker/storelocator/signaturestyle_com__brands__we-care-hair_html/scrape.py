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
    locator_domain = "https://www.signaturestyle.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(
        "https://www.signaturestyle.com/brands/we-care-hair.html", headers=headers
    )
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="other-salon"]')
    for d in div:

        page_url = "".join(d.xpath('.//a[text()="SALON DETAILS"]/@href'))
        street_address = "".join(d.xpath('.//span[@class="streetAddress1"]/text()'))
        city = (
            "".join(d.xpath('.//span[@class="addressLocality1"]/text()'))
            .replace(",", "")
            .strip()
        )
        state = (
            "".join(d.xpath('.//span[@class="addressRegion1"]/text()'))
            .split()[0]
            .strip()
        )
        postal = (
            "".join(d.xpath('.//span[@class="addressRegion1"]/text()'))
            .split()[1]
            .strip()
        )
        location_name = "".join(d.xpath('.//div[@class="store-loc"]/text()'))
        country_code = "US"
        store_number = "<MISSING>"
        latitude = (
            "".join(d.xpath('.//a[text()="DIRECTIONS"]/@href'))
            .split("saddr=")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(d.xpath('.//a[text()="DIRECTIONS"]/@href'))
            .split("saddr=")[1]
            .split(",")[1]
            .split("&")[0]
            .strip()
        )
        location_type = "We Care Hair"
        hours_of_operation = "<MISSING>"
        phone = "<MISSING>"

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
