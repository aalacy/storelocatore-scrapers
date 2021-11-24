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

    locator_domain = "https://www.colemans.ca"
    page_url = "https://www.colemans.ca/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "one-third location ")]')
    for d in div:

        location_name = "".join(d.xpath(".//h3/text()"))
        location_type = "<MISSING>"
        street_address = "".join(d.xpath(".//p[1]/text()[1]"))
        state = (
            "".join(d.xpath(".//p[1]/text()[2]"))
            .replace("\n", "")
            .split(",")[1]
            .strip()
        )
        postal = "".join(d.xpath(".//p[1]/text()[3]")).replace("\n", "").strip()
        country_code = "CA"
        city = (
            "".join(d.xpath(".//p[1]/text()[2]"))
            .replace("\n", "")
            .split(",")[0]
            .strip()
        )
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = "".join(
            d.xpath(".//strong[text()='Phone:']/following-sibling::text()[1]")
        ).strip()
        hours_of_operation = (
            " ".join(d.xpath(".//table//tr/td//text()")).replace("\n", "").strip()
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
