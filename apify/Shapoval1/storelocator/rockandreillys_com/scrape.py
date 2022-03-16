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

    locator_domain = "https://rockandreillys.com/"
    api_url = "https://rockandreillys.com/"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    tree = html.fromstring(r.text)
    div = tree.xpath('//h3[text()="Address"]')
    for d in div:

        page_url = "https://rockandreillys.com/"
        street_address = "".join(d.xpath(".//following-sibling::p[1]/text()[1]"))
        ad = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        store_number = "<MISSING>"
        location_name = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        country_code = "US"
        location_type = "rockandreillys"
        phone = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[3]"))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = "".join(
            d.xpath('.//following::p[contains(text(), "Monday")]/text()')
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
