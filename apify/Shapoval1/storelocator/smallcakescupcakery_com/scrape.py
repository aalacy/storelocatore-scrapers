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

    locator_domain = "https://www.smallcakescupcakery.com"
    page_url = "https://www.smallcakescupcakery.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-item"]')
    for d in div:
        location_name = "".join(d.xpath('.//span[@class="location-locale"]/text()'))
        location_type = "<MISSING>"
        street_address = (
            "".join(d.xpath('.//span[@class="location-address"]/text()')) or "<MISSING>"
        )
        if location_name.find("Coming Soon") != -1:
            location_type = "Coming Soon"
            location_name = location_name.split("--")[0].strip()
        if location_name.find("--") != -1:
            location_name = location_name.split("--")[0].strip()
        phone = "".join(d.xpath('.//a[contains(@href,"tel")]/text()')) or "<MISSING>"
        state = (
            "".join(d.xpath('.//span[@class="location-state"]/text()')) or "<MISSING>"
        )
        postal = (
            "".join(d.xpath('.//span[@class="location-zip"]/text()')) or "<MISSING>"
        )
        country_code = "US"
        city = "".join(d.xpath('.//span[@class="location-city"]/text()')) or "<MISSING>"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
