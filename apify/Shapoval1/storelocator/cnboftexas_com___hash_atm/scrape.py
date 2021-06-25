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

    locator_domain = "https://www.cnboftexas.com/"
    page_url = "https://www.cnboftexas.com/atm-locations/"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.post(page_url, headers=headers)

    tree = html.fromstring(r.text)
    div = tree.xpath("//div[@class='locations-container atm']")

    for d in div:
        street_address = (
            "".join(
                d.xpath('.//div[@class="locations-name"]/following-sibling::text()[1]')
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                d.xpath('.//div[@class="locations-name"]/following-sibling::text()[2]')
            )
            .replace("\n", "")
            .strip()
        )
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        location_name = (
            "".join(d.xpath('.//div[@class="locations-name"]/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        store_number = (
            "".join(
                d.xpath('.//following::script[contains(text(), "var branch")]/text()')
            )
            .split(f"{location_name}")[1]
            .split(",")[3]
            .strip()
        )
        latitude = (
            "".join(
                d.xpath('.//following::script[contains(text(), "var branch")]/text()')
            )
            .split(f"{location_name}")[1]
            .split(",")[1]
            .strip()
        )
        longitude = (
            "".join(
                d.xpath('.//following::script[contains(text(), "var branch")]/text()')
            )
            .split(f"{location_name}")[1]
            .split(",")[2]
            .strip()
        )
        country_code = "US"
        location_type = "ATM"
        phone = "<MISSING>"
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
